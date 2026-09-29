from sqlalchemy.orm import Session
from backend.models.evidence import Evidence
from backend.ai.extraction import ExtractedEvidenceItem
import json

class EvidenceRepository:
    def __init__(self, db: Session):
        self.db = db

    def save_extracted(self, den_id: str, material_id: str, modality: str, item: ExtractedEvidenceItem) -> Evidence:
        metadata = {
            "start_time": item.start_time,
            "end_time": item.end_time,
            "page_number": item.page_number,
            "region": item.region
        }
        
        evidence = Evidence(
            den_id=den_id,
            material_id=material_id,
            modality=modality,
            content=item.content,
            content_type=item.content_type,
            confidence=item.confidence,
            metadata_json=metadata
        )
        self.db.add(evidence)
        self.db.commit()
        self.db.refresh(evidence)
        return evidence

    def get_den_evidence(self, den_id: str) -> list[Evidence]:
        return self.db.query(Evidence).filter(Evidence.den_id == den_id).all()

    def get_rock_evidence(self, rock_id: str) -> list[Evidence]:
        from backend.models.material import Material
        return self.db.query(Evidence).join(Material, Evidence.material_id == Material.id).filter(Material.rock_id == rock_id).all()
