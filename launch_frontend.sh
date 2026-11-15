#!/usr/bin/env bash
# ================================================================
#  ContractRisk AI Frontend Launcher (macOS / Linux)
#  Group 2: Gursirat Singh (12326116) & Rounak Azad (12326217)
# ================================================================

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd "$DIR"

echo ""
echo "  ====================================================="
echo "   ContractRisk AI -- Multi-Agent Contract Review UI"
echo "   Group 2: Gursirat Singh (12326116)"
echo "            Rounak Azad   (12326217)"
echo "  ====================================================="
echo ""

if [ -d ".venv" ]; then
    echo "  Activating virtual environment (.venv)..."
    source .venv/bin/activate
fi

echo "  Starting Streamlit frontend..."
echo "  Open your browser at: http://localhost:8501"
echo ""

streamlit run frontend_app.py --server.port 8501

