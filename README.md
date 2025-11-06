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


## Frontend (React) details
The `frontend/` folder is a Vite + React + Konva app that implements a professional drag-and-drop canvas.
To build the frontend bundle (so the Streamlit app can load it):

```bash
cd frontend
npm install
npm run build
```

After building, run the Streamlit app from the project root:

```bash
pip install -r requirements.txt
streamlit run app.py
```

The Streamlit app will load `frontend/build/index.html` and show the full canvas UI.
