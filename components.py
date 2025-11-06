import os
import streamlit as st
import streamlit.components.v1 as components
from pathlib import Path

def load_frontend_component(key='dlsim'):
    # If frontend build exists at frontend/build/index.html, load it into an iframe via components.html
    build_dir = Path(__file__).parent / 'frontend' / 'build'
    index_file = build_dir / 'index.html'
    if index_file.exists():
        html = index_file.read_text(encoding='utf-8')
        # Serve the built HTML via components.html (iframe)
        components.html(html, height=700, scrolling=True, key=key)
        return True
    else:
        st.warning('Frontend build not found. Please run `npm run build` in the frontend/ folder per README.')
        return False
