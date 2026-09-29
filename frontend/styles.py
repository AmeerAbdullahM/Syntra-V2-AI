"""
Syntra V2 - Transparent Universe Design System
"""

SYNTRA_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

/* Base Styles & Typography */
html, body, [class*="css"] {
    font-family: 'Inter', sans-serif !important;
}

/* Make the entire Streamlit app transparent so the 3D Universe shows through */
.stApp {
    background: transparent !important;
    color: #e2e8f0 !important;
}

/* Hide Streamlit Branding */
[data-testid="stDecoration"] { display: none !important; }
#MainMenu { visibility: hidden; }
footer { visibility: hidden; }
header { visibility: hidden; }

/* Main Content Padding */
.main .block-container {
    padding-top: 3rem !important;
    padding-left: 3rem !important;
    padding-right: 3rem !important;
    max-width: 1200px !important;
}

/* Sidebar - Extremely subtle glassmorphism or just completely transparent */
[data-testid="stSidebar"] {
    background-color: rgba(5, 5, 16, 0.4) !important;
    backdrop-filter: blur(8px) !important;
    -webkit-backdrop-filter: blur(8px) !important;
    border-right: 1px solid rgba(255, 255, 255, 0.05) !important;
}

/* Sidebar Navigation Items */
[data-testid="stSidebarNav"] a {
    border-radius: 8px;
    margin: 4px 12px;
    padding: 10px 16px !important;
    font-size: 0.9rem !important;
    font-weight: 500 !important;
    color: #94a3b8 !important;
    transition: all 0.2s ease !important;
}
[data-testid="stSidebarNav"] a:hover {
    background: rgba(255, 255, 255, 0.05) !important;
    color: #f8fafc !important;
}
[data-testid="stSidebarNav"] a[aria-current="page"] {
    background: transparent !important;
    color: #22d3ee !important; /* Cyan active state */
    font-weight: 600 !important;
    border-left: 3px solid #22d3ee;
}

/* COMPLETELY REMOVE CONTAINERS, BORDERS, and BOX-SHADOWS */
[data-testid="stVerticalBlockBorderWrapper"], .stContainer, [data-testid="stForm"] {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    padding: 0 !important;
}

/* Inputs - make them elegant and minimalistic */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea,
.stSelectbox > div > div,
.stNumberInput > div > div > input {
    background: rgba(255, 255, 255, 0.03) !important;
    border: none !important;
    border-bottom: 2px solid rgba(255, 255, 255, 0.1) !important;
    border-radius: 4px 4px 0 0 !important;
    color: #f1f5f9 !important;
    font-size: 1rem !important;
    padding: 0.75rem 1rem !important;
    transition: all 0.2s ease !important;
}
.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {
    background: rgba(255, 255, 255, 0.08) !important;
    border-bottom-color: #22d3ee !important;
    box-shadow: none !important;
}

/* Input Labels - use distinct colors */
.stTextInput > label,
.stTextArea > label,
.stSelectbox > label,
.stNumberInput > label {
    font-size: 0.85rem !important;
    font-weight: 500 !important;
    color: #818cf8 !important; /* Indigo text to differentiate sections */
    margin-bottom: 0.2rem !important;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

/* Buttons - Primary */
.stButton > button[kind="primary"], 
.stFormSubmitButton > button {
    background: transparent !important;
    color: #22d3ee !important;
    border: 1px solid #22d3ee !important;
    border-radius: 30px !important;
    padding: 0.6rem 2rem !important;
    font-weight: 600 !important;
    font-size: 0.95rem !important;
    transition: all 0.3s ease !important;
    box-shadow: 0 0 10px rgba(34, 211, 238, 0.1) !important;
    width: 100%;
}
.stButton > button[kind="primary"]:hover,
.stFormSubmitButton > button:hover {
    background: rgba(34, 211, 238, 0.15) !important;
    box-shadow: 0 0 20px rgba(34, 211, 238, 0.4) !important;
}

/* Buttons - Secondary */
.stButton > button[kind="secondary"] {
    background: transparent !important;
    color: #94a3b8 !important;
    border: 1px solid rgba(255, 255, 255, 0.15) !important;
    border-radius: 30px !important;
    padding: 0.6rem 2rem !important;
    font-weight: 500 !important;
    transition: all 0.3s ease !important;
}
.stButton > button[kind="secondary"]:hover {
    color: #e2e8f0 !important;
    border-color: rgba(255, 255, 255, 0.4) !important;
    background: rgba(255, 255, 255, 0.05) !important;
}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    background: transparent !important;
    border-bottom: 1px solid rgba(255, 255, 255, 0.1) !important;
    gap: 3rem !important;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    color: #64748b !important;
    font-size: 1rem !important;
    font-weight: 500 !important;
    padding: 1rem 0 !important;
    border-bottom: 2px solid transparent !important;
    transition: all 0.2s ease !important;
}
.stTabs [aria-selected="true"] {
    color: #22d3ee !important;
    border-bottom-color: #22d3ee !important;
    font-weight: 600 !important;
    text-shadow: 0 0 10px rgba(34, 211, 238, 0.3);
}

/* Expanders */
[data-testid="stExpander"] {
    background: transparent !important;
    border: none !important;
    border-bottom: 1px solid rgba(255, 255, 255, 0.1) !important;
    border-radius: 0 !important;
}
[data-testid="stExpander"] summary {
    font-weight: 600 !important;
    color: #818cf8 !important;
}

/* Typography elements */
h1 { font-size: 3rem !important; font-weight: 300 !important; color: #f8fafc !important; letter-spacing: 0.05em !important; }
h2 { font-size: 1.8rem !important; font-weight: 300 !important; color: #cbd5e1 !important; }
h3 { font-size: 1.3rem !important; font-weight: 400 !important; color: #e2e8f0 !important; }
p { color: #94a3b8 !important; line-height: 1.6 !important; font-weight: 300 !important; }

/* Custom Badges */
.badge-admin {
    color: #22d3ee;
    font-size: 0.75rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.1em;
}
.badge-member {
    color: #cbd5e1;
    font-size: 0.75rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.1em;
}
</style>
"""
