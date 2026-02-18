#!/usr/bin/env python3
"""PharmaClaw Web API — FastAPI backend wrapping existing agent scripts.

Endpoints:
  POST /api/chemistry   — Compound lookup + properties + retrosynthesis
  POST /api/pharmacology — ADME/PK profiling
  POST /api/catalyst     — Catalyst recommendation + ligand design
  GET  /api/health       — Health check

Deploy on Render: scripts are bundled in api/skills/
"""

import json
import os
import subprocess
import sys
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional

app = FastAPI(title="PharmaClaw API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Script paths — bundled in api/skills/ for deployment
API_DIR = Path(__file__).parent
CHEM_SCRIPTS = API_DIR / "skills" / "chemistry"
PHARMA_SCRIPTS = API_DIR / "skills" / "pharmacology"
CATALYST_SCRIPTS = API_DIR / "skills" / "catalyst"


def run_script(script_path: Path, args: list[str], timeout: int = 30) -> dict:
    """Run a Python script and return parsed JSON output."""
    if not script_path.exists():
        raise HTTPException(status_code=500, detail=f"Script not found: {script_path.name}")

    cmd = [sys.executable, str(script_path)] + args
    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=timeout,
            cwd=str(script_path.parent)
        )
        if result.returncode != 0:
            error_msg = result.stderr.strip() or result.stdout.strip() or "Unknown error"
            return {"status": "error", "error": error_msg}

        output = result.stdout.strip()
        if not output:
            return {"status": "error", "error": "No output from script"}
        return json.loads(output)
    except subprocess.TimeoutExpired:
        return {"status": "error", "error": "Request timed out (30s)"}
    except json.JSONDecodeError:
        return {"status": "success", "raw": result.stdout.strip()}
    except Exception as e:
        return {"status": "error", "error": str(e)}


# --- Request Models ---

class ChemistryRequest(BaseModel):
    compound: str = Field(..., description="Drug name, SMILES string, or PubChem CID")
    include_retro: bool = Field(default=True, description="Include retrosynthesis analysis")
    retro_depth: int = Field(default=2, ge=1, le=4, description="Retrosynthesis depth")

class PharmacologyRequest(BaseModel):
    compound: str = Field(..., description="Drug name or SMILES string")

class CatalystRequest(BaseModel):
    reaction: Optional[str] = Field(None, description="Reaction type (e.g., suzuki, C-N coupling)")
    scaffold: Optional[str] = Field(None, description="Ligand SMILES or name (PPh3, NHC_IMes, etc.)")
    strategy: str = Field(default="all", description="Ligand modification strategy")
    enantioselective: bool = Field(default=False)
    prefer_earth_abundant: bool = Field(default=False)


# --- Endpoints ---

@app.get("/api/health")
def health():
    return {"status": "ok", "version": "1.0.0", "agents": ["chemistry", "pharmacology", "catalyst"]}


@app.post("/api/chemistry")
def chemistry_query(req: ChemistryRequest):
    """Run Chemistry Query agent: PubChem lookup + RDKit properties + retrosynthesis."""
    results = {}

    # 1. PubChem info
    info = run_script(CHEM_SCRIPTS / "query_pubchem.py", [
        "--compound", req.compound, "--type", "info"
    ])

    # Flatten nested PubChem response for frontend
    if isinstance(info, dict) and "PropertyTable" in info:
        props_list = info["PropertyTable"].get("Properties", [])
        results["pubchem"] = props_list[0] if props_list else info
    else:
        results["pubchem"] = info

    # 2. Get SMILES
    smiles = None
    if isinstance(info, dict) and info.get("status") != "error":
        smiles = info.get("CanonicalSMILES") or info.get("smiles")
        if not smiles and "PropertyTable" in info:
            props_list = info["PropertyTable"].get("Properties", [])
            if props_list:
                smiles = props_list[0].get("CanonicalSMILES")

    # Fetch structure explicitly if needed
    if not smiles and isinstance(info, dict) and info.get("status") != "error":
        struct = run_script(CHEM_SCRIPTS / "query_pubchem.py", [
            "--compound", req.compound, "--type", "structure", "--format", "smiles"
        ])
        if isinstance(struct, dict):
            smiles = struct.get("result") or struct.get("smiles") or struct.get("CanonicalSMILES")
            if not smiles and struct.get("raw"):
                smiles = struct["raw"].strip()

    # If input looks like SMILES, use directly
    if not smiles and any(c in req.compound for c in "()=#[]@"):
        smiles = req.compound

    # 3. RDKit properties
    if smiles:
        props = run_script(CHEM_SCRIPTS / "rdkit_mol.py", [
            "--smiles", smiles, "--action", "props"
        ])
        results["properties"] = props

        # 4. Retrosynthesis
        if req.include_retro:
            retro = run_script(CHEM_SCRIPTS / "rdkit_mol.py", [
                "--target", smiles, "--action", "retro", "--depth", str(req.retro_depth)
            ])
            results["retrosynthesis"] = retro
    else:
        results["note"] = "Could not resolve SMILES. Try entering a SMILES string directly."

    results["query"] = req.compound
    results["smiles"] = smiles
    return results


@app.post("/api/pharmacology")
def pharmacology_query(req: PharmacologyRequest):
    """Run Pharmacology agent: ADME/PK profiling."""
    input_json = json.dumps({"name": req.compound, "context": "web_ui"})

    if any(c in req.compound for c in "()=#[]@"):
        input_json = json.dumps({"smiles": req.compound, "context": "web_ui"})

    result = run_script(PHARMA_SCRIPTS / "chain_entry.py", [
        "--input-json", input_json
    ])
    return result


@app.post("/api/catalyst")
def catalyst_query(req: CatalystRequest):
    """Run Catalyst Design agent: recommendation + ligand design."""
    if not req.reaction and not req.scaffold:
        raise HTTPException(status_code=400, detail="Provide either 'reaction' or 'scaffold' (or both)")

    input_data = {"context": "web_ui"}
    if req.reaction:
        input_data["reaction"] = req.reaction
    if req.scaffold:
        input_data["scaffold"] = req.scaffold
    input_data["strategy"] = req.strategy
    input_data["enantioselective"] = req.enantioselective
    if req.prefer_earth_abundant:
        input_data["constraints"] = {"prefer_earth_abundant": True}

    result = run_script(CATALYST_SCRIPTS / "chain_entry.py", [
        "--input-json", json.dumps(input_data)
    ])
    return result


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
