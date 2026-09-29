import streamlit as st
from frontend.session import require_auth, get_current_user
from backend.database.connection import SessionLocal
from backend.services.den.den_service import DenService, DenServiceError
from backend.services.rock.rock_service import RockService, RockServiceError
from backend.services.material.material_service import MaterialService
from backend.schemas.rock import RockCreate

require_auth()
user = get_current_user()

den_id = st.session_state.get("current_den_id")

if not den_id:
    st.markdown("""
        <div style="text-align: center; padding: 5rem 2rem; margin-top: 2rem;">
            <h2 style="color: #f8fafc; margin-bottom: 0.5rem;">No learning Den selected</h2>
            <p style="color: #cbd5e1; font-size: 1rem; max-width: 400px; margin: 0 auto 2rem auto;">
                Select a Den from My Dens to view its collaborative learning workspace, access materials, and join discussions.
            </p>
        </div>
    """, unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1,1,1])
    with col2:
        if st.button("Go to My Dens", use_container_width=True, type="primary"):
            st.switch_page("pages/dens.py")
    st.stop()

def get_status_color(status):
    status = status.upper() if status else "UNKNOWN"
    if status == "COMPLETED": return "#10b981"
    if status == "EXTRACTING": return "#f59e0b"
    if status == "FAILED": return "#ef4444"
    return "#94a3b8"

def render_materials_section(rock_id: str, is_admin: bool, db):
    material_service = MaterialService(db)
    materials = material_service.get_rock_materials(rock_id, user)
    
    st.markdown("<h4 style='margin-top: 1.5rem; margin-bottom: 1rem; font-size: 1rem; color: #e2e8f0;'>Materials</h4>", unsafe_allow_html=True)
    
    if not materials:
        st.markdown("""
            <div style="padding: 1rem; text-align: center;">
                <p style="color: #94a3b8; font-size: 0.9rem; margin: 0;">No materials uploaded yet.</p>
            </div>
        """, unsafe_allow_html=True)
    else:
        for m in materials:
            col_m1, col_m2 = st.columns([3, 2])
            with col_m1:
                # Use standard button, style via CSS if needed
                if st.button(f"{m.original_filename}", key=f"mat_btn_{m.id}", use_container_width=True):
                    st.session_state.view_material_id = m.id
                    st.switch_page("pages/view_material.py")
            with col_m2:
                status_col = get_status_color(m.processing_status)
                st.markdown(f"""
                    <div style="display: flex; align-items: center; height: 100%; font-size: 0.85rem;">
                        <span style="color: #94a3b8; margin-right: 12px;">{m.modality}</span>
                        <span style="background: {status_col}20; color: {status_col}; padding: 2px 8px; border-radius: 12px; font-weight: 600; font-size: 0.7rem; border: 1px solid {status_col}40;">
                            {m.processing_status}
                        </span>
                    </div>
                """, unsafe_allow_html=True)

    if is_admin:
        st.markdown("<div style='margin-top: 1rem;'></div>", unsafe_allow_html=True)
        with st.expander("Upload New Material"):
            with st.form(f"upload_form_{rock_id}"):
                uploaded_files = st.file_uploader("Select Files", key=f"uploader_{rock_id}", accept_multiple_files=True, help="Supports Audio, Image, PDF, TXT")
                st.markdown("<div style='margin-top: 0.5rem;'></div>", unsafe_allow_html=True)
                up_btn = st.form_submit_button("Upload Selected Files")
                if up_btn and uploaded_files:
                    with st.spinner(f"Uploading {len(uploaded_files)} file(s)..."):
                        for uploaded_file in uploaded_files:
                            try:
                                material_service.upload_material(
                                    den_id=den_id,
                                    rock_id=rock_id,
                                    user=user,
                                    filename=uploaded_file.name,
                                    mime_type=uploaded_file.type,
                                    content=uploaded_file,
                                    size_bytes=uploaded_file.size
                                )
                                st.success(f"Uploaded {uploaded_file.name} successfully!")
                            except Exception as e:
                                st.error(f"Error uploading {uploaded_file.name}: {str(e)}")
                    st.rerun()

with SessionLocal() as db:
    den_service = DenService(db)
    rock_service = RockService(db)
    
    try:
        den = den_service.get_den(den_id, user)
        is_admin = den_service.is_admin(den_id, user)
        
        col_hdr1, col_hdr2 = st.columns([4, 1])
        with col_hdr1:
            role_badge = "badge-admin" if is_admin else "badge-member"
            role_text = "ADMIN" if is_admin else "MEMBER"
            st.markdown(f"""
                <div style="display: flex; align-items: center; gap: 1rem; margin-bottom: 0.5rem;">
                    <h1 style="margin: 0;">{den.name}</h1>
                    <span class="{role_badge}">{role_text}</span>
                </div>
            """, unsafe_allow_html=True)
            if den.description:
                st.markdown(f"<p style='color: #cbd5e1; font-size: 1.05rem;'>{den.description}</p>", unsafe_allow_html=True)
        with col_hdr2:
            if st.button("My Dens", use_container_width=True):
                st.switch_page("pages/dens.py")
            
        st.markdown("<div style='margin-top: 1rem;'></div>", unsafe_allow_html=True)
        
        tabs = st.tabs(["Rocks", "Evidence", "Conflicts", "Concepts", "Artifacts", "Q&A", "Members", "Settings"])
        
        with tabs[0]:
            if is_admin:
                with st.expander("Create New Rock"):
                    with st.form("create_rock_form"):
                        r_title = st.text_input("Rock Title", placeholder="e.g. Unit 1: Introduction")
                        r_desc = st.text_area("Description", placeholder="What will this rock contain?")
                        r_order = st.number_input("Order Index", value=0, min_value=0)
                        st.markdown("<div style='margin-top: 1rem;'></div>", unsafe_allow_html=True)
                        if st.form_submit_button("Create Rock"):
                            if not r_title:
                                st.error("Rock title is required.")
                            else:
                                with st.spinner("Creating rock..."):
                                    try:
                                        rock_service.create_rock(
                                            RockCreate(den_id=den_id, title=r_title, description=r_desc, order_index=r_order), 
                                            user
                                        )
                                        st.success("Rock created successfully!")
                                        st.rerun()
                                    except RockServiceError as e:
                                        st.error(str(e))
            
            rocks = rock_service.get_den_rocks(den_id, user)
            if not rocks:
                st.markdown("""
                    <div style="text-align: center; padding: 3rem 1rem; margin-top: 1rem;">
                        <p style="color: #94a3b8; font-size: 1.1rem; margin: 0;">No Rocks exist in this Den yet.</p>
                        <p style="color: #64748b; font-size: 0.9rem; margin-top: 0.5rem;">Rocks are containers for your materials and discussions.</p>
                    </div>
                """, unsafe_allow_html=True)
            else:
                for rock in rocks:
                    with st.container(border=True):
                        col_r1, col_r2 = st.columns([4, 1])
                        with col_r1:
                            st.markdown(f"<h3 style='margin-bottom: 0.25rem;'>{rock.title}</h3>", unsafe_allow_html=True)
                            if rock.description:
                                st.markdown(f"<p style='color: #94a3b8; font-size: 0.95rem; margin-bottom: 0;'>{rock.description}</p>", unsafe_allow_html=True)
                        with col_r2:
                            if is_admin:
                                if st.button("Delete", key=f"del_rock_{rock.id}", help="Delete Rock"):
                                    rock_service.delete_rock(rock.id, user)
                                    st.rerun()
                                    
                        render_materials_section(rock.id, is_admin, db)
                        
                        if is_admin:
                            st.divider()
                            col_a, col_b = st.columns(2)
                            with col_a:
                                if st.button("Run Fusion Pipeline", key=f"fuse_{rock.id}", use_container_width=True):
                                    with st.spinner("Initiating alignment and fusion..."):
                                        try:
                                            rock_service.trigger_fusion(rock.id, user)
                                            st.success("Fusion enqueued! Check Concepts shortly.")
                                        except RockServiceError as e:
                                            st.error(str(e))
                            with col_b:
                                if st.button("Generate Cheat Sheet", key=f"artifact_{rock.id}", use_container_width=True):
                                    from backend.services.artifact.artifact_service import ArtifactService
                                    a_service = ArtifactService(db)
                                    with st.spinner("Generating artifact..."):
                                        try:
                                            a_service.generate_cheat_sheet(den_id, rock.id, user)
                                            st.success("Cheat Sheet generated!")
                                            st.rerun()
                                        except Exception as e:
                                            st.error(str(e))
            
        with tabs[1]:
            from backend.database.repositories.evidence_repo import EvidenceRepository
            ev_repo = EvidenceRepository(db)
            rocks = rock_service.get_den_rocks(den_id, user)
            
            if not rocks:
                st.info("No rocks found to display evidence.")
            else:
                has_ev = False
                for rock in rocks:
                    evs = ev_repo.get_rock_evidence(rock.id)
                    if evs: has_ev = True
                    with st.expander(f"{rock.title} ({len(evs)} items)"):
                        if not evs:
                            st.write("No evidence extracted yet.")
                        for e in evs:
                            col_e1, col_e2 = st.columns([4, 1])
                            with col_e1:
                                conf_val = 0.0
                                conf_display = "Unknown Confidence"
                                conf_color = "#f59e0b"
                                if e.confidence:
                                    try:
                                        conf_val = float(e.confidence)
                                        conf_display = f"{conf_val:.2f} Confidence"
                                        conf_color = "#10b981" if conf_val > 0.8 else "#f59e0b"
                                    except ValueError:
                                        conf_display = f"{e.confidence} Confidence"
                                        conf_color = "#10b981" if str(e.confidence).upper() in ["HIGH", "CERTAIN"] else "#f59e0b"
                                
                                st.markdown(f"""
                                    <div style="margin-bottom: 0.5rem;">
                                        <span style="color: #94a3b8; font-size: 0.8rem; text-transform: uppercase;">{e.modality}</span>
                                        <span style="color: {conf_color}; font-size: 0.8rem; margin-left: 12px; font-weight: 600;">{conf_display}</span>
                                    </div>
                                    <div style="padding: 1rem; border-left: 3px solid #3b82f6; color: #e2e8f0;">
                                        {e.content}
                                    </div>
                                """, unsafe_allow_html=True)
                            with col_e2:
                                if is_admin:
                                    if st.button("Delete", key=f"del_ev_{e.id}"):
                                        db.delete(e)
                                        db.commit()
                                        st.rerun()
                            st.markdown("<hr style='border-color: rgba(255,255,255,0.05);'/>", unsafe_allow_html=True)
                if not has_ev:
                    st.info("No evidence has been extracted across any Rocks yet.")
                            
        with tabs[2]:
            from backend.models.evidence import EvidenceRelation, Evidence
            rocks = rock_service.get_den_rocks(den_id, user)
            if not rocks:
                st.info("No rocks found.")
            else:
                has_conflict = False
                for rock in rocks:
                    conflicts = db.query(EvidenceRelation).filter(
                        EvidenceRelation.rock_id == rock.id,
                        EvidenceRelation.relationship == "CONTRADICTS",
                        EvidenceRelation.is_resolved == 0
                    ).all()
                    
                    if conflicts: has_conflict = True
                    with st.expander(f"{rock.title} ({len(conflicts)} unresolved)"):
                        if not conflicts:
                            st.write("No unresolved conflicts.")
                        else:
                            for conflict in conflicts:
                                src = db.query(Evidence).filter(Evidence.id == conflict.source_evidence_id).first()
                                tgt = db.query(Evidence).filter(Evidence.id == conflict.target_evidence_id).first()
                                
                                st.markdown(f"""
                                    <div style="background: rgba(239, 68, 68, 0.1); border-left: 4px solid #ef4444; padding: 1rem; border-radius: 4px; margin-bottom: 1rem;">
                                        <h4 style="margin: 0 0 0.5rem 0; color: #fca5a5;">Contradiction Detected</h4>
                                        <p style="margin: 0; color: #e2e8f0; font-style: italic;">{conflict.reasoning}</p>
                                    </div>
                                """, unsafe_allow_html=True)
                                
                                col_c1, col_c2 = st.columns(2)
                                with col_c1:
                                    st.markdown(f"**Source ({src.modality if src else 'N/A'})**")
                                    st.caption(src.content if src else 'Deleted')
                                with col_c2:
                                    st.markdown(f"**Target ({tgt.modality if tgt else 'N/A'})**")
                                    st.caption(tgt.content if tgt else 'Deleted')
                                    
                                if is_admin:
                                    with st.form(f"resolve_conflict_{conflict.id}"):
                                        res_note = st.text_input("Admin Clarification", placeholder="Provide clarity...")
                                        if st.form_submit_button("Resolve Conflict"):
                                            if res_note:
                                                conflict.is_resolved = 1
                                                conflict.resolution_note = res_note
                                                db.commit()
                                                st.success("Resolved!")
                                                st.rerun()
                                            else:
                                                st.error("Provide a clarification note.")
                                st.divider()
                if not has_conflict:
                    st.markdown("""
                        <div style="text-align: center; padding: 3rem 1rem;">
                            <p style="color: #94a3b8;">No data conflicts detected in this Den.</p>
                        </div>
                    """, unsafe_allow_html=True)

        with tabs[3]:
            from backend.models.fusion import FusedConcept
            rocks = rock_service.get_den_rocks(den_id, user)
            if not rocks:
                st.info("No rocks found.")
            else:
                has_concept = False
                for rock in rocks:
                    concepts = db.query(FusedConcept).filter(FusedConcept.rock_id == rock.id).all()
                    if concepts: has_concept = True
                    with st.expander(f"{rock.title} ({len(concepts)} concepts)"):
                        if not concepts:
                            st.write("No concepts synthesized yet.")
                        for c in concepts:
                            col_c1, col_c2 = st.columns([4, 1])
                            with col_c1:
                                st.markdown(f"**{c.title}** <span style='font-size:0.8rem;color:#94a3b8;'>({c.alignment_status})</span>", unsafe_allow_html=True)
                                st.markdown(f"<div style='color:#e2e8f0;margin:0.5rem 0;'>{c.explanation}</div>", unsafe_allow_html=True)
                            with col_c2:
                                if is_admin:
                                    if st.button("Delete", key=f"del_c_{c.id}"):
                                        db.delete(c)
                                        db.commit()
                                        st.rerun()
                            st.divider()
                if not has_concept:
                    st.info("No concepts fused yet. Run the Fusion Pipeline on a Rock.")

        with tabs[4]:
            from backend.models.artifact import Artifact
            rocks = rock_service.get_den_rocks(den_id, user)
            if not rocks:
                st.info("No rocks found.")
            else:
                has_art = False
                for rock in rocks:
                    artifacts = db.query(Artifact).filter(Artifact.rock_id == rock.id).all()
                    if artifacts: has_art = True
                    with st.expander(f"{rock.title} ({len(artifacts)} items)"):
                        if not artifacts:
                            st.write("No artifacts generated yet.")
                        for a in artifacts:
                            col_a1, col_a2 = st.columns([4, 1])
                            with col_a1:
                                st.markdown(f"**{a.title}**")
                                with st.container(border=True):
                                    st.markdown(a.content_markdown)
                            with col_a2:
                                if is_admin:
                                    if st.button("Delete", key=f"del_art_{a.id}"):
                                        db.delete(a)
                                        db.commit()
                                        st.rerun()
                            st.divider()
                if not has_art:
                    st.info("No artifacts exist yet. Admins can generate them from the Rocks tab.")

        with tabs[5]:
            from backend.services.qa.qa_service import QAService
            qa_service = QAService(db)
            
            with st.container(border=True):
                with st.form("ask_q_form"):
                    q_text = st.text_input("Ask a question about the materials in this Den...", placeholder="e.g. What are the main takeaways from Unit 1?")
                    col_qbtn, _ = st.columns([1, 4])
                    with col_qbtn:
                        q_sub = st.form_submit_button("Ask Syntra", type="primary")
                    if q_sub:
                        if q_text:
                            with st.spinner("Syntra AI is synthesizing an answer..."):
                                qa_service.post_question(den_id, user, q_text)
                            st.rerun()
                        else:
                            st.error("Please enter a question.")
                            
            st.markdown("<div style='margin-top: 2rem;'></div>", unsafe_allow_html=True)
            threads = qa_service.get_den_threads(den_id)
            if not threads:
                st.markdown("""
                    <div style="text-align: center; padding: 2rem; opacity: 0.7;">
                        <p style="color: #94a3b8;">No questions asked yet. Be the first!</p>
                    </div>
                """, unsafe_allow_html=True)
            else:
                for t in threads:
                    with st.expander(t.question):
                        if is_admin:
                            if st.button("Delete Thread", key=f"del_qa_{t.id}"):
                                db.delete(t)
                                db.commit()
                                st.rerun()
                        msgs = qa_service.get_thread_messages(t.id)
                        for m in msgs:
                            if m.is_ai == "true":
                                st.markdown(f"""
                                    <div style="background: rgba(99, 102, 241, 0.1); border-left: 3px solid #6366f1; padding: 1rem; border-radius: 0 8px 8px 0; margin: 0.5rem 0;">
                                        <div style="font-size: 0.8rem; color: #818cf8; font-weight: 600; margin-bottom: 0.25rem;">SYNTRA AI</div>
                                        <div style="color: #e2e8f0;">{m.content}</div>
                                    </div>
                                """, unsafe_allow_html=True)
                            else:
                                st.markdown(f"""
                                    <div style="background: rgba(255, 255, 255, 0.03); padding: 1rem; border-radius: 8px; margin: 0.5rem 0;">
                                        <div style="font-size: 0.8rem; color: #94a3b8; font-weight: 600; margin-bottom: 0.25rem;">STUDENT</div>
                                        <div style="color: #cbd5e1;">{m.content}</div>
                                    </div>
                                """, unsafe_allow_html=True)
            
        with tabs[6]:
            members_info = den_service.get_members_with_info(den_id)
            
            if not members_info:
                st.write("No members found.")
            else:
                for m in members_info:
                    with st.container(border=True):
                        col_m1, col_m2 = st.columns([3, 1])
                        with col_m1:
                            m_badge = "badge-admin" if m['role'] == "ADMIN" else "badge-member"
                            st.markdown(f"""
                                <div style="display:flex; align-items:center; gap:0.75rem; margin-bottom:0.25rem;">
                                    <span style="font-weight:600; font-size:1.1rem;">{m['display_name']}</span>
                                    <span class="{m_badge}">{m['role']}</span>
                                </div>
                                <div style="color:#94a3b8; font-size:0.9rem;">{m['email']}</div>
                            """, unsafe_allow_html=True)
                        
                        with col_m2:
                            if is_admin and m['user_id'] != user.id:
                                if st.button("Remove", key=f"rm_{m['user_id']}", use_container_width=True):
                                    with st.spinner("Removing..."):
                                        try:
                                            den_service.remove_member(den_id, m['user_id'], user)
                                            st.success(f"Removed {m['display_name']}")
                                            st.rerun()
                                        except DenServiceError as e:
                                            st.error(str(e))
                                            
                                if st.button("Ban User", key=f"ban_{m['user_id']}", use_container_width=True):
                                    with st.spinner("Banning..."):
                                        try:
                                            den_service.ban_member(den_id, m['user_id'], user)
                                            st.success(f"Banned {m['display_name']}")
                                            st.rerun()
                                        except DenServiceError as e:
                                            st.error(str(e))
                
        with tabs[7]:
            if is_admin:
                st.markdown("<h3>Pending Join Requests</h3>", unsafe_allow_html=True)
                reqs = den_service.get_join_requests(den_id, user)
                if not reqs:
                    st.info("No pending requests.")
                else:
                    for req in reqs:
                        with st.container(border=True):
                            col_req_1, col_req_2, col_req_3 = st.columns([2,1,1])
                            with col_req_1:
                                st.write(f"**User ID:** {req.user_id}")
                            with col_req_2:
                                if st.button("Approve", key=f"app_{req.id}", use_container_width=True):
                                    den_service.resolve_join_request(req.id, True, user)
                                    st.rerun()
                            with col_req_3:
                                if st.button("Reject", key=f"rej_{req.id}", use_container_width=True):
                                    den_service.resolve_join_request(req.id, False, user)
                                    st.rerun()
                                
                st.divider()
                st.markdown("<h3 style='color: #ef4444;'>Danger Zone</h3>", unsafe_allow_html=True)
                st.markdown("""
                    <div style="background: rgba(239, 68, 68, 0.1); border: 1px solid rgba(239, 68, 68, 0.3); padding: 1rem; border-radius: 8px; margin-bottom: 1rem;">
                        <strong style="color: #fca5a5;">Warning:</strong> Deleting this Den will permanently remove all Rocks, Materials, and Data. This action cannot be undone.
                    </div>
                """, unsafe_allow_html=True)
                
                if st.button("Delete Den Permanently", type="primary"):
                    with st.spinner("Deleting Den..."):
                        den_service.delete_den(den_id, user)
                        st.session_state.current_den_id = None
                        st.switch_page("pages/dens.py")
            else:
                st.markdown("<h3>Leave Den</h3>", unsafe_allow_html=True)
                st.warning("If you leave, you will need to request access or use an invite code to rejoin.")
                if st.button("Leave Den", type="primary"):
                    with st.spinner("Leaving..."):
                        try:
                            den_service.leave_den(den_id, user)
                            st.session_state.current_den_id = None
                            st.switch_page("pages/dens.py")
                        except DenServiceError as e:
                            st.error(str(e))
            
    except DenServiceError as e:
        st.error(str(e))
        if st.button("Back to Dens"):
            st.switch_page("pages/dens.py")
