# Digital Logic Simulator — Streamlit Port (Verified)

This is a verified, runnable Streamlit-based prototype of a digital logic simulator.

## Quick start (local)
1. python -m venv .venv
2. source .venv/bin/activate   (Linux/macOS) or .\.venv\Scripts\activate (Windows)
3. pip install -r requirements.txt
4. streamlit run app.py
5. Open http://localhost:8501

## Docker
docker build -t logic-sim .
docker run -p 8501:8501 logic-sim

## What I verified
- Logic operations for AND, OR, NOT, NAND, NOR, XOR implemented and tested.
- Topological evaluation order and cycle detection.
- INPUT gates retain assigned values and OUTPUT reads connected input.
- Isolated gates evaluate sensibly (INPUT returns assigned value; other isolated gates -> False).
