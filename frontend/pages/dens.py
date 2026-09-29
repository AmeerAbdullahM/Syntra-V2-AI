import streamlit as st
from frontend.session import require_auth, get_current_user
from backend.database.connection import SessionLocal
from backend.services.den.den_service import DenService, DenServiceError
from backend.schemas.den import DenCreate
from backend.database.repositories.den_repo import DenRepository

require_auth()
user = get_current_user()

st.markdown("""
    <div style="margin-bottom: 2rem;">
        <h1 style="margin-bottom: 0.25rem;">My Dens</h1>
        <p style="color: #94a3b8; font-size: 1rem;">Create a new workspace or join an existing learning community.</p>
    </div>
""", unsafe_allow_html=True)

with SessionLocal() as db:
    den_service = DenService(db)
    den_repo = DenRepository(db)
    
    col_create, col_join = st.columns([1, 1], gap="large")
    
    with col_create:
        st.markdown("<h2>Create a New Den</h2>", unsafe_allow_html=True)
        with st.container(border=True):
            with st.form("create_den_form"):
                name = st.text_input("Den Name", placeholder="e.g. Advanced Machine Learning")
                description = st.text_area("Description (Optional)", placeholder="What is this Den about?", height=100)
                
                col_vis, col_code = st.columns(2)
                with col_vis:
                    is_public_choice = st.radio("Visibility", ["Public", "Private"], help="Private dens require an invite code.")
                with col_code:
                    invite_code = st.text_input("Invite Code", placeholder="Required if Private")
                    
                limit_members = st.checkbox("Limit maximum members?")
                max_members = st.number_input("Max Members", min_value=1, value=50, disabled=not limit_members)
                
                st.markdown("<div style='margin-top: 1rem;'></div>", unsafe_allow_html=True)
                submit = st.form_submit_button("Create Den")
                
                if submit:
                    if not name:
                        st.error("Den Name is required.")
                    elif is_public_choice == "Private" and not invite_code:
                        st.error("Invite Code is required for Private Dens.")
                    else:
                        with st.spinner("Creating Den..."):
                            try:
                                den_create = DenCreate(
                                    name=name, 
                                    description=description,
                                    is_public=(is_public_choice == "Public"),
                                    invite_code=invite_code if is_public_choice == "Private" else None,
                                    max_members=max_members if limit_members else None
                                )
                                new_den = den_service.create_den(den_create, user)
                                st.success(f"Den '{new_den.name}' created successfully!")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error creating Den: {e}")
                    
    with col_join:
        st.markdown("<h2>Join a Den</h2>", unsafe_allow_html=True)
        
        tab_pub, tab_priv = st.tabs(["Public Dens", "Private Den"])
        
        user_dens = den_service.get_user_dens(user)
        joined_ids = [d['den'].id for d in user_dens]
        all_dens = den_repo.list_all()
        
        with tab_pub:
            public_dens = [d for d in all_dens if d.id not in joined_ids and d.is_public == "true"]
            
            with st.container(border=True):
                if public_dens:
                    with st.form("join_pub_den_form"):
                        den_to_join = st.selectbox("Select a Public Den to Join", options=public_dens, format_func=lambda d: d.name)
                        st.markdown("<div style='margin-top: 1rem;'></div>", unsafe_allow_html=True)
                        join_submit = st.form_submit_button("Request to Join")
                        
                        if join_submit:
                            with st.spinner("Sending request..."):
                                try:
                                    den_service.request_to_join_den(den_to_join.id, user)
                                    st.success(f"Request sent to join '{den_to_join.name}'!")
                                except DenServiceError as e:
                                    st.error(str(e))
                else:
                    st.markdown("""
                        <div style="text-align: center; padding: 2rem 1rem;">
                            <p style="color: #94a3b8; font-size: 0.95rem; margin: 0;">No new public Dens available to join.</p>
                        </div>
                    """, unsafe_allow_html=True)
                
        with tab_priv:
            private_dens = [d for d in all_dens if d.id not in joined_ids and d.is_public == "false"]
            
            with st.container(border=True):
                if private_dens:
                    with st.form("join_priv_den_form"):
                        den_to_join_priv = st.selectbox("Select Private Den", options=private_dens, format_func=lambda d: d.name)
                        priv_code = st.text_input("Invite Code", type="password", placeholder="Enter the secret code")
                        st.markdown("<div style='margin-top: 1rem;'></div>", unsafe_allow_html=True)
                        join_priv_submit = st.form_submit_button("Join Private Den")
                        
                        if join_priv_submit:
                            if not priv_code:
                                st.error("Please enter the invite code.")
                            else:
                                with st.spinner("Verifying code..."):
                                    try:
                                        den_service.join_den_with_code(den_to_join_priv.id, priv_code, user)
                                        st.success(f"Successfully joined '{den_to_join_priv.name}'!")
                                        st.rerun()
                                    except DenServiceError as e:
                                        st.error(str(e))
                else:
                    st.markdown("""
                        <div style="text-align: center; padding: 2rem 1rem;">
                            <p style="color: #94a3b8; font-size: 0.95rem; margin: 0;">No private Dens available.</p>
                        </div>
                    """, unsafe_allow_html=True)
