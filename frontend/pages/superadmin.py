import streamlit as st
from frontend.session import require_auth, get_current_user
from backend.database.connection import SessionLocal
from backend.config.settings import settings

require_auth()
user = get_current_user()

if user.email != settings.SUPERADMIN_EMAIL:
    st.error("You are not authorized to view this page.")
    st.stop()

st.title("Super Admin Control Facility")
st.markdown("Full control over Users and Dens.")

tab_users, tab_dens = st.tabs(["Manage Users", "Manage Dens"])

with SessionLocal() as db:
    from backend.database.repositories.user_repo import UserRepository
    from backend.services.den.den_service import DenService
    
    user_repo = UserRepository(db)
    den_service = DenService(db)
    
    with tab_users:
        st.subheader("All Users")
        users = user_repo.get_all()
        
        for u in users:
            with st.container(border=True):
                cols = st.columns([3, 2, 2, 2])
                cols[0].write(f"**{u.display_name}**")
                cols[1].write(u.email)
                cols[2].caption(f"ID: {u.id[:8]}...")
                
                if u.email == settings.SUPERADMIN_EMAIL:
                    cols[3].caption("SUPERADMIN")
                else:
                    if cols[3].button("Delete User", key=f"del_user_{u.id}", type="primary"):
                        user_repo.delete_user(u.id)
                        st.success(f"Deleted user {u.display_name}")
                        st.rerun()
                        
    with tab_dens:
        st.subheader("All Dens")
        dens = den_service.den_repo.list_all()
        
        for d in dens:
            with st.container(border=True):
                st.write(f"### {d.name}")
                st.caption(f"ID: {d.id} | Members: {len(den_service.membership_repo.get_den_members(d.id))}")
                
                # List members for this den so admin can ban/remove
                members = den_service.get_members_with_info(d.id)
                for m in members:
                    m_cols = st.columns([3, 2, 2, 2])
                    m_cols[0].write(m['display_name'])
                    m_cols[1].write(m['email'])
                    m_cols[2].caption(f"Role: {m['role']}")
                    if m_cols[3].button("Remove", key=f"remove_user_{m['user_id']}_den_{d.id}"):
                        den_service.membership_repo.remove_member(m['user_id'], d.id)
                        st.success("Member removed.")
                        st.rerun()
                        
                if st.button("Delete Entire Den", key=f"del_den_{d.id}", type="primary"):
                    den_service.den_repo.delete(d.id)
                    st.success(f"Deleted Den {d.name}")
                    st.rerun()
