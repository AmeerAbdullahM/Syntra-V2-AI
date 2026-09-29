import streamlit as st
import os
from backend.database.connection import SessionLocal
from backend.database.repositories.material_repo import MaterialRepository
from backend.config.settings import settings
from frontend.session import require_auth

require_auth()

col_back, col_sp = st.columns([1, 4])
with col_back:
    if st.button("Back to Den", use_container_width=True):
        st.switch_page("pages/den_view.py")

material_id = st.session_state.get("view_material_id")

if not material_id:
    st.markdown("""
        <div style="text-align: center; padding: 5rem 2rem; margin-top: 2rem;">
            <h2 style="color: #f8fafc; margin-bottom: 0.5rem;">No material selected</h2>
            <p style="color: #cbd5e1; font-size: 1rem; max-width: 400px; margin: 0 auto;">
                Materials shared within your Den will appear here when you open them.
            </p>
        </div>
    """, unsafe_allow_html=True)
    st.stop()

with SessionLocal() as db:
    mat_repo = MaterialRepository(db)
    material = mat_repo.get_by_id(material_id)
    
    if not material:
        st.error("Material not found. It may have been deleted.")
        st.stop()
        
    file_path = os.path.normpath(os.path.join(settings.LOCAL_STORAGE_PATH, material.stored_filename))
    
    if not os.path.exists(file_path):
        st.error("File not available on disk.")
        st.stop()
        
    # Material header
    st.markdown(f"""
        <div style="margin-bottom: 1.5rem; margin-top: 1rem;">
            <h1 style="margin-bottom: 4px;">{material.original_filename}</h1>
            <div style="display: flex; gap: 1rem; color: #94a3b8; font-size: 0.85rem; font-weight: 500;">
                <span style="background: rgba(255,255,255,0.05); padding: 4px 10px; border-radius: 6px;">Type: {material.modality}</span>
                <span style="background: rgba(255,255,255,0.05); padding: 4px 10px; border-radius: 6px;">MIME: {material.mime_type}</span>
                <span style="background: rgba(99, 102, 241, 0.1); color: #818cf8; padding: 4px 10px; border-radius: 6px;">Status: {material.processing_status}</span>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    with open(file_path, "rb") as f:
        bytes_data = f.read()
        
    st.download_button(
        label="Download Material",
        data=bytes_data,
        file_name=material.original_filename,
        mime=material.mime_type
    )
    st.divider()
    
    with st.spinner("Loading material..."):
        mime_type = material.mime_type or ""
        if mime_type.startswith("image/"):
            st.image(file_path, use_column_width=True)
            
        elif mime_type.startswith("audio/"):
            st.audio(file_path)
            
        elif mime_type.startswith("video/"):
            st.video(file_path)
            
        elif mime_type == "application/pdf":
            import base64
            base64_pdf = base64.b64encode(bytes_data).decode('utf-8')
            pdf_display = (
                f'<iframe src="data:application/pdf;base64,{base64_pdf}" '
                f'width="100%" height="800px" type="application/pdf" '
                f'style="border:1px solid rgba(255,255,255,0.1); border-radius:8px;"></iframe>'
            )
            st.markdown(pdf_display, unsafe_allow_html=True)
            
        else:
            try:
                text_content = bytes_data.decode("utf-8", errors="replace")
                ext = material.original_filename.rsplit(".", 1)[-1].lower() if "." in material.original_filename else ""
                lang_map = {
                    "py": "python", "js": "javascript", "ts": "typescript",
                    "json": "json", "html": "html", "css": "css",
                    "md": "markdown", "txt": None, "csv": None
                }
                lang = lang_map.get(ext, None)
                
                st.markdown("""
                    <div style="padding: 10px 15px; border-bottom: none; display: flex; justify-content: space-between; align-items: center;">
                        <span style="color: #94a3b8; font-size: 0.8rem; font-family: monospace;">Source Viewer</span>
                    </div>
                """, unsafe_allow_html=True)
                
                st.code(text_content, language=lang)
            except Exception:
                st.warning("Unable to render this file type in the browser. Please download it directly.")
