import streamlit as st
from typing import Dict, Any

def render_sidebar_config(model_params: Dict[str, Any]) -> Dict[str, Any]:
    """Render sidebar configuration controls"""
    st.sidebar.subheader("⚙️ Model Configuration")
    
    updated_params = {
        "temperature": st.sidebar.slider(
            "Temperature",
            min_value=0.0,
            max_value=1.0,
            value=model_params.get("temperature", 0.7),
            step=0.1,
            help="Controls randomness in responses"
        ),
        "context_length": st.sidebar.slider(
            "Context Length",
            min_value=512,
            max_value=4096,
            value=model_params.get("context_length", 2048),
            step=128,
            help="Maximum context length for the model"
        ),
        "top_k": st.sidebar.slider(
            "Top K",
            min_value=1,
            max_value=100,
            value=model_params.get("top_k", 40),
            help="Number of top tokens to consider"
        ),
        "retrieval_k": st.sidebar.slider(
            "Retrieval K",
            min_value=1,
            max_value=10,
            value=model_params.get("retrieval_k", 3),
            help="Number of documents to retrieve"
        ),
        "model_name": model_params.get("model_name", "llama2")
    }
    
    return updated_params

def render_chess_package_explorer(metadata: Dict[str, Any]):
    """Render the chess package explorer"""
    st.sidebar.subheader("📚 Chess Engine Components")
    
    if not metadata or "packages" not in metadata:
        st.sidebar.warning("No package information available")
        return
    
    for package in metadata["packages"]:
        with st.sidebar.expander(f"📦 {package.get('package_name', 'Unknown')}"):
            st.write(f"**Purpose**: {package.get('purpose', 'N/A')}")
            
            if package.get("routines"):
                st.write("**Routines:**")
                for routine in package["routines"]:
                    routine_type = routine.get("type", "").title()
                    routine_name = routine.get("name", "")
                    routine_params = routine.get("parameters", "")
                    st.code(f"{routine_type}: {routine_name}({routine_params})")
