import time
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database.connection import SessionLocal
from backend.queue.postgres_queue import PostgresQueue
from backend.models.job import JobTypeEnum
from backend.database.repositories.material_repo import MaterialRepository
from backend.database.repositories.evidence_repo import EvidenceRepository
from backend.ai.extraction import ExtractionService
from backend.storage.factory import get_storage
from backend.config.settings import settings

def process_material_job(db, job_info):
    print(f"Processing material job: {job_info['job_id']}")
    material_id = job_info['payload']['material_id']
    
    mat_repo = MaterialRepository(db)
    material = mat_repo.get_by_id(material_id)
    if not material:
        raise Exception("Material not found")
        
    mat_repo.update_status(material_id, "EXTRACTING")
    
    storage = get_storage()
    # In local storage, we can get the real path by just constructing it.
    # For a real implementation, we'd probably download it to a temp file, 
    # but since local storage is on disk, we can pass the path directly to Gemini API.
    # Note: If it was S3, we'd download it to a temp dir first.
    if settings.STORAGE_BACKEND == "local":
        file_path = os.path.normpath(os.path.join(settings.LOCAL_STORAGE_PATH, material.stored_filename))
    else:
        raise NotImplementedError("Only local storage worker supported in this phase")

    if not settings.GEMINI_API_KEY:
        print("No GEMINI_API_KEY. Simulating extraction...")
        time.sleep(2)
        # Mock evidence
        ev_repo = EvidenceRepository(db)
        from backend.ai.extraction import ExtractedEvidenceItem
        ev_repo.save_extracted(
            den_id=material.den_id,
            material_id=material.id,
            modality=material.modality,
            item=ExtractedEvidenceItem(
                content="This is simulated evidence since no API key is provided.",
                content_type="transcript",
                confidence="MEDIUM"
            )
        )
    else:
        # Real extraction
        extractor = ExtractionService()
        result = extractor.extract_evidence(file_path, material.mime_type, material.modality)
        
        ev_repo = EvidenceRepository(db)
        for item in result.items:
            ev_repo.save_extracted(
                den_id=material.den_id,
                material_id=material.id,
                modality=material.modality,
                item=item
            )
            
    print(f"Completed material job: {job_info['job_id']}")

def process_fusion_job(db, job_info):
    print(f"Processing fusion job: {job_info['job_id']}")
    rock_id = job_info['payload']['rock_id']
    den_id = job_info['den_id']
    
    from backend.database.repositories.evidence_repo import EvidenceRepository
    from backend.ai.alignment import AlignmentService
    from backend.ai.fusion import FusionService
    from backend.models.fusion import FusedConcept
    
    ev_repo = EvidenceRepository(db)
    evidence_list = ev_repo.get_rock_evidence(rock_id)
    
    if not evidence_list:
        print("No evidence to fuse.")
        return
        
    print(f"Aligning {len(evidence_list)} evidence items...")
    aligner = AlignmentService()
    alignment_result = aligner.align_evidence(evidence_list)
    
    print("Fusing concepts...")
    fuser = FusionService()
    fusion_result = fuser.fuse_evidence(evidence_list, alignment_result.relations)
    
    # Save relations to DB
    from backend.models.evidence import EvidenceRelation
    for r in alignment_result.relations:
        # Check if source and target exist in evidence_list to ensure integrity
        ev_ids = [e.id for e in evidence_list]
        if r.source_evidence_id in ev_ids and r.target_evidence_id in ev_ids:
            relation = EvidenceRelation(
                den_id=den_id,
                rock_id=rock_id,
                source_evidence_id=r.source_evidence_id,
                target_evidence_id=r.target_evidence_id,
                relationship=r.relationship,
                confidence=r.confidence,
                reasoning=r.reasoning
            )
            db.add(relation)
            
    # Remove existing fused concepts for this rock so we don't get duplicates on re-run
    db.query(FusedConcept).filter(FusedConcept.rock_id == rock_id).delete()
    
    for c in fusion_result.concepts:
        concept = FusedConcept(
            den_id=den_id,
            rock_id=rock_id,
            title=c.title,
            explanation=c.explanation,
            confidence=c.confidence,
            alignment_status=c.alignment_status,
            evidence_ids=c.evidence_ids,
            accessibility_description=c.accessibility_description
        )
        db.add(concept)
    
    db.commit()
    print("Fusion job completed successfully.")

def main():
    print("Worker started. Listening for jobs...")
    while True:
        with SessionLocal() as db:
            queue = PostgresQueue(db)
            job_info = queue.dequeue(JobTypeEnum.MATERIAL_PROCESS.value)
            
            if job_info:
                try:
                    process_material_job(db, job_info)
                    queue.complete(job_info["job_id"])
                    
                    repo = MaterialRepository(db)
                    repo.update_status(job_info["target_id"], "COMPLETED")
                    
                except Exception as e:
                    print(f"Job failed: {e}")
                    queue.fail(job_info["job_id"], str(e))
                    
                    repo = MaterialRepository(db)
                    repo.update_status(job_info["target_id"], "FAILED", failure_reason=str(e))
                continue

            job_info = queue.dequeue(JobTypeEnum.ROCK_FUSION.value)
            if job_info:
                try:
                    process_fusion_job(db, job_info)
                    queue.complete(job_info["job_id"])
                except Exception as e:
                    print(f"Fusion Job failed: {e}")
                    queue.fail(job_info["job_id"], str(e))
                continue
                
            time.sleep(2)

if __name__ == "__main__":
    main()
