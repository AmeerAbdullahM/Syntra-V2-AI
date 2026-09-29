import streamlit as st
from frontend.session import require_auth, get_current_user
from backend.database.connection import SessionLocal
from backend.services.den.den_service import DenService

require_auth()
user = get_current_user()

st.markdown(f"""
    <div style="margin-bottom: 2rem;">
        <h1 style="margin-bottom: 0.25rem;">Welcome back, {user.display_name}</h1>
        <p style="color: #94a3b8; font-size: 1rem;">Here's an overview of your active learning spaces.</p>
    </div>
""", unsafe_allow_html=True)

with SessionLocal() as db:
    den_service = DenService(db)
    user_dens = den_service.get_user_dens(user)
    
    col1, col2 = st.columns([4, 1])
    with col1:
        st.markdown("<h2>Your Learning Dens</h2>", unsafe_allow_html=True)
    with col2:
        if st.button("Create Den", use_container_width=True, type="primary"):
            st.switch_page("pages/dens.py")
    
    if not user_dens:
        st.markdown("""
            <div style="text-align: center; padding: 4rem 2rem; margin-top: 1rem;">
                <h3 style="margin-bottom: 0.5rem; color: #f8fafc;">No learning Dens yet</h3>
                <p style="color: #cbd5e1; margin-bottom: 1.5rem;">Dens are collaborative spaces for your study materials and discussions.</p>
            </div>
        """, unsafe_allow_html=True)
        col_empty1, col_empty2, col_empty3 = st.columns([1, 1, 1])
        with col_empty2:
            if st.button("Create your first Den", use_container_width=True, type="primary"):
                st.switch_page("pages/dens.py")
    else:
        st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)
        cols_per_row = 3
        for i in range(0, len(user_dens), cols_per_row):
            row_dens = user_dens[i:i+cols_per_row]
            cols = st.columns(cols_per_row)
            for j, col in enumerate(cols):
                if j < len(row_dens):
                    item = row_dens[j]
                    den = item['den']
                    role = item['role']
                    member_count = len(den_service.membership_repo.get_den_members(den.id))
                    
                    with col:
                        with st.container(border=True):
                            badge_class = "badge-admin" if role == "ADMIN" else "badge-member"
                            role_display = "Admin" if role == "ADMIN" else "Member"
                            visibility_icon = "Public" if den.is_public == "true" else "Private"
                            
                            st.markdown(f"""
                                <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 0.75rem;">
                                    <h3 style="margin: 0; font-size: 1.25rem; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width: 70%;">{den.name}</h3>
                                    <span class="{badge_class}">{role_display}</span>
                                </div>
                            """, unsafe_allow_html=True)
                            
                            if den.description:
                                desc = den.description[:85] + "..." if len(den.description) > 85 else den.description
                                st.markdown(f"<p style='min-height: 3rem; margin-bottom: 1rem; font-size: 0.9rem;'>{desc}</p>", unsafe_allow_html=True)
                            else:
                                st.markdown("<p style='min-height: 3rem; margin-bottom: 1rem; font-size: 0.9rem; font-style: italic; opacity: 0.7;'>No description provided.</p>", unsafe_allow_html=True)
                            
                            st.markdown(f"""
                                <div style="display: flex; gap: 1rem; margin-bottom: 1rem; font-size: 0.85rem; color: #94a3b8;">
                                    <span>{member_count} member{'s' if member_count != 1 else ''}</span>
                                    <span>{visibility_icon}</span>
                                </div>
                            """, unsafe_allow_html=True)
                            
                            if st.button("Enter Workspace", key=f"dash_enter_{den.id}", type="primary", use_container_width=True):
                                st.session_state.current_den_id = den.id
                                st.switch_page("pages/den_view.py")
