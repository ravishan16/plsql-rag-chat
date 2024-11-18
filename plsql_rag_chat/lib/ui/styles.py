# plsql_rag_chat/lib/ui/styles.py
CUSTOM_CSS = """
<style>
    /* Dark mode optimization */
    .dark {
        background-color: #1E1E1E;
        color: #E0E0E0;
    }
    
    /* Improved chat container */
    .stChatFloatingInputContainer {
        bottom: 20px;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    /* Enhanced message styling */
    .stChatMessage {
        padding: 1rem;
        margin-bottom: 1rem;
        border-radius: 0.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        transition: transform 0.2s;
    }
    
    .stChatMessage:hover {
        transform: translateY(-2px);
    }
    
    /* Improved code blocks */
    .st-code {
        padding: 1.2rem !important;
        margin: 1.2rem 0 !important;
        border-radius: 0.5rem !important;
        background: #2D2D2D !important;
        font-family: 'JetBrains Mono', monospace !important;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
"""