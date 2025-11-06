import streamlit as st
from streamlit_drawable_canvas import st_canvas
from sim import Circuit, Gate
import uuid
from PIL import Image, ImageDraw, ImageFont

# --- FastAPI backend for simulation and persistence ---
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import threading
import uvicorn
import json as _json
from pathlib import Path

api = FastAPI()
api.add_middleware(CORSMiddleware, allow_origins=['*'], allow_methods=['*'], allow_headers=['*'])

DATA_DIR = Path(__file__).parent / 'data'
DATA_DIR.mkdir(exist_ok=True)

@api.post('/evaluate')
async def evaluate_circuit(payload: dict):
    # expected payload: { nodes: [...], edges: [...] , inputs: {id: bool, ...} (optional) }
    try:
        nodes = payload.get('nodes', [])
        edges = payload.get('edges', [])
        # build circuit
        from sim import Circuit, Gate
        c = Circuit()
        for n in nodes:
            g = Gate(n['id'], n['type'])
            c.add_gate(g)
        for e in edges:
            # default to pin 'a' for connections
            c.connect(e['from'], e['to'], 'a')
        inputs = payload.get('inputs', {})
        for iid, val in inputs.items():
            if iid in c.gates:
                try:
                    c.set_input_value(iid, bool(val))
                except Exception:
                    pass
        vals = c.evaluate()
        try:
            import networkx as _nx
            order = list(_nx.topological_sort(c.G))
        except Exception:
            order = list(vals.keys())
        return {'values': vals, 'order': order}
        return {'values': vals}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))

@api.post('/save')
async def save_circuit(payload: dict):
    name = payload.get('name') or ('circuit_' + str(len(list(DATA_DIR.iterdir()))+1))
    path = DATA_DIR / (name + '.json')
    path.write_text(_json.dumps(payload, indent=2))
    return {'saved': str(path.name)}

@api.get('/list')
async def list_circuits():
    files = [p.name for p in DATA_DIR.glob('*.json')]
    return {'files': files}

@api.get('/load')
async def load_circuit(name: str):
    path = DATA_DIR / name
    if not path.exists():
        raise HTTPException(status_code=404, detail='Not found')
    return _json.loads(path.read_text())

def run_api():
    uvicorn.run(api, host='0.0.0.0', port=8000, log_level='info')

# start API in background thread if not already started
if 'api_thread_started' not in globals():
    t = threading.Thread(target=run_api, daemon=True)
    t.start()
    globals()['api_thread_started'] = True
# --- end FastAPI backend ---


st.set_page_config(page_title="Digital Logic Sim (Streamlit)", layout="wide")

# Attempt to load frontend build (if present) for a full-featured canvas UI.
try:
    from components import load_frontend_component
    built = load_frontend_component()
    if built:
        # if frontend served, stop further Streamlit UI (frontend handles UI)
        st.stop()
except Exception:
    pass



def new_id(prefix="g"):
    import uuid as _uuid
    return f"{prefix}_{_uuid.uuid4().hex[:8]}"

def ensure_state():
    if "circuit" not in st.session_state:
        st.session_state.circuit = Circuit()
    if "nodes" not in st.session_state:
        st.session_state.nodes = {}
    if "mode" not in st.session_state:
        st.session_state.mode = "select"
    if "connect_src" not in st.session_state:
        st.session_state.connect_src = None
    if "last_eval" not in st.session_state:
        st.session_state.last_eval = {}

ensure_state()

col_left, col_canvas, col_right = st.columns([1, 3, 1])

with col_left:
    st.header("Palette")
    if st.button("INPUT"):
        gid = new_id("in")
        g = Gate(gid, "INPUT", position=(50,50))
        st.session_state.circuit.add_gate(g)
        st.session_state.nodes[gid] = {"type":"INPUT","x":50,"y":50,"w":100,"h":50}
    if st.button("OUTPUT"):
        gid = new_id("out")
        g = Gate(gid, "OUTPUT", position=(150,50))
        st.session_state.circuit.add_gate(g)
        st.session_state.nodes[gid] = {"type":"OUTPUT","x":200,"y":50,"w":100,"h":50}
    if st.button("AND"):
        gid = new_id("and")
        g = Gate(gid, "AND", position=(50,150))
        st.session_state.circuit.add_gate(g)
        st.session_state.nodes[gid] = {"type":"AND","x":50,"y":150,"w":100,"h":50}
    if st.button("OR"):
        gid = new_id("or")
        g = Gate(gid, "OR", position=(150,150))
        st.session_state.circuit.add_gate(g)
        st.session_state.nodes[gid] = {"type":"OR","x":150,"y":150,"w":100,"h":50}
    if st.button("NOT"):
        gid = new_id("not")
        g = Gate(gid, "NOT", position=(250,150))
        st.session_state.circuit.add_gate(g)
        st.session_state.nodes[gid] = {"type":"NOT","x":250,"y":150,"w":80,"h":40}

    st.markdown('---')
    if st.radio("Mode", ["select","connect"] , index=0) == "connect":
        st.session_state.mode = "connect"
    else:
        st.session_state.mode = "select"

    if st.session_state.mode == "connect":
        st.write("Click a source gate then a destination gate to connect.")
        if st.button("Clear selection"):
            st.session_state.connect_src = None

    st.markdown('---')
    st.write("Inputs")
    for gid, node in list(st.session_state.nodes.items()):
        if node["type"] == "INPUT":
            val = st.checkbox(f"{gid}", value=bool(st.session_state.circuit.gates[gid].value), key=f"chk_{gid}")
            st.session_state.circuit.set_input_value(gid, val)

    if st.button("Evaluate"):
        try:
            vals = st.session_state.circuit.evaluate()
            st.session_state.last_eval = vals
            st.success("Evaluated")
        except Exception as e:
            st.error(str(e))

    if st.button("Clear All"):
        st.session_state.circuit.clear()
        st.session_state.nodes = {}
        st.session_state.connect_src = None
        st.session_state.last_eval = {}

with col_canvas:
    st.header("Canvas")
    canvas_width = 900
    canvas_height = 600
    bg = Image.new("RGBA",(canvas_width,canvas_height),(255,255,255,255))
    draw = ImageDraw.Draw(bg)
    font = None
    try:
        font = ImageFont.truetype("DejaVuSans.ttf", 14)
    except Exception:
        from PIL import ImageFont as _ImageFont
        font = _ImageFont.load_default()
    for gid, node in st.session_state.nodes.items():
        x = node["x"]; y = node["y"]; w = node.get("w",100); h = node.get("h",50)
        rect = [x,y,x+w,y+h]
        val = bool(st.session_state.last_eval.get(gid, False)) if st.session_state.last_eval else None
        fill = (240,240,240,255)
        if node["type"] == "INPUT":
            fill = (220,255,220,255) if val else (255,230,230,255)
        elif node["type"] == "OUTPUT":
            fill = (200,200,255,255) if val else (240,240,255,255)
        draw.rectangle(rect, fill=fill, outline=(0,0,0))
        draw.text((x+6,y+6), f"{node['type']}\n{gid[:8]}", font=font, fill=(0,0,0))
    for src, dst, data in st.session_state.circuit.G.edges(data=True):
        src_node = st.session_state.nodes.get(src)
        dst_node = st.session_state.nodes.get(dst)
        if src_node and dst_node:
            sx = src_node["x"] + src_node.get("w",100)
            sy = src_node["y"] + src_node.get("h",50)/2
            dx = dst_node["x"]
            dy = dst_node["y"] + dst_node.get("h",50)/2
            draw.line((sx,sy,dx,dy), fill=(60,60,60), width=3)
            draw.text(((sx+dx)/2, (sy+dy)/2-10), data.get("pin","a"), font=font, fill=(0,0,0))

    canvas_result = st_canvas(
        fill_color="rgba(0,0,0,0)",
        stroke_width=2,
        stroke_color="#000000",
        background_image=bg,
        height=canvas_height,
        width=canvas_width,
        drawing_mode="transform",
        key="canvas",
    )

    st.write("Canvas controls:")
    cols = st.columns([1,1,1,1])
    if cols[0].button("Select by ID"):
        st.session_state.select_id = st.text_input("Enter gate id to select", "")
    nud_cols = st.columns([1,1,1,1,1])
    if nud_cols[0].button("←"):
        sid = st.session_state.get("select_id")
        if sid and sid in st.session_state.nodes:
            st.session_state.nodes[sid]["x"] -= 10
    if nud_cols[1].button("→"):
        sid = st.session_state.get("select_id")
        if sid and sid in st.session_state.nodes:
            st.session_state.nodes[sid]["x"] += 10
    if nud_cols[2].button("↑"):
        sid = st.session_state.get("select_id")
        if sid and sid in st.session_state.nodes:
            st.session_state.nodes[sid]["y"] -= 10
    if nud_cols[3].button("↓"):
        sid = st.session_state.get("select_id")
        if sid and sid in st.session_state.nodes:
            st.session_state.nodes[sid]["y"] += 10
    if nud_cols[4].button("Delete"):
        sid = st.session_state.get("select_id")
        if sid and sid in st.session_state.nodes:
            try:
                st.session_state.circuit.remove_gate(sid)
            except:
                pass
            del st.session_state.nodes[sid]
            st.session_state.select_id = None

with col_right:
    st.header("Inspector")
    st.write("Nodes")
    for gid, node in st.session_state.nodes.items():
        with st.expander(f"{gid} - {node['type']}"):
            st.write("pos:", node["x"], node["y"])
            if st.button(f"Select {gid}", key=f"sel_{gid}"):
                st.session_state.select_id = gid
            if st.session_state.mode == "connect":
                if st.button(f"Set source {gid}", key=f"src_{gid}"):
                    st.session_state.connect_src = gid
                if st.button(f"Connect to {gid}", key=f"dst_{gid}"):
                    src = st.session_state.connect_src
                    if src and src != gid:
                        try:
                            st.session_state.circuit.connect(src, gid, "a")
                            st.success(f"Connected {src} -> {gid}")
                        except Exception as e:
                            st.error(str(e))
                    else:
                        st.warning("Select a source first")
            st.write("Gate eval value:", st.session_state.last_eval.get(gid) if st.session_state.last_eval else None)

st.sidebar.markdown("## Controls")
st.sidebar.write("Use the left palette to add gates. Use connect mode to connect gates. Toggle INPUT checkboxes and Evaluate.")
