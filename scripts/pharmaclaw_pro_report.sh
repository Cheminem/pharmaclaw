#!/bin/bash
# Usage: ./pharmaclaw_pro_report.sh "SMILES1" "SMILES2" ["SMILES3"] [--names "A,B,C"] [--output report.pdf]
# Chains compound_comparison.py → pdf_report.py for PharmaClaw Pro reports.

set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Find Python with rdkit
if [ -d "$SCRIPT_DIR/../rdkit_env" ]; then
  PYTHON="$SCRIPT_DIR/../rdkit_env/bin/python"
elif command -v python3 &>/dev/null && python3 -c "import rdkit" 2>/dev/null; then
  PYTHON="python3"
elif [ -d "$HOME/rdkit_env" ]; then
  PYTHON="$HOME/rdkit_env/bin/python"
else
  echo "Error: No Python environment with RDKit found." >&2
  echo "Install rdkit_env or ensure 'python3 -c \"import rdkit\"' works." >&2
  exit 1
fi

# Parse args: separate SMILES from flags
SMILES_ARGS=()
NAMES=""
OUTPUT="pharmaclaw_report_$(date +%Y-%m-%d).pdf"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --names) NAMES="$2"; shift 2 ;;
    --output) OUTPUT="$2"; shift 2 ;;
    --*) echo "Unknown option: $1" >&2; exit 1 ;;
    *) SMILES_ARGS+=("$1"); shift ;;
  esac
done

if [ ${#SMILES_ARGS[@]} -lt 2 ]; then
  echo "Usage: $0 \"SMILES1\" \"SMILES2\" [\"SMILES3\"] [--names \"A,B,C\"] [--output report.pdf]" >&2
  exit 1
fi

# Build comparison command
COMP_CMD=("$PYTHON" "$SCRIPT_DIR/compound_comparison.py")
for s in "${SMILES_ARGS[@]}"; do
  COMP_CMD+=("$s")
done
[ -n "$NAMES" ] && COMP_CMD+=(--names "$NAMES")

# Run comparison, pipe JSON to PDF report generator
"${COMP_CMD[@]}" | "$PYTHON" "$SCRIPT_DIR/pdf_report.py" --output "$OUTPUT"

echo "✅ Report saved: $OUTPUT"
