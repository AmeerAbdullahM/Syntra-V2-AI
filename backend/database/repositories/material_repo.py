from sqlalchemy.orm import Session
from backend.models.material import Material
from backend.schemas.material import MaterialCreate
from typing import List

class MaterialRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, data: MaterialCreate) -> Material:
        material = Material(
            den_id=data.den_id,
            rock_id=data.rock_id,
            uploader_id=data.uploader_id,
            original_filename=data.original_filename,
            stored_filename=data.stored_filename,
            mime_type=data.mime_type,
            size_bytes=data.size_bytes,
            checksum=data.checksum,
            modality=data.modality
        )
        self.db.add(material)
        self.db.commit()
        self.db.refresh(material)
        return material

    def get_by_id(self, material_id: str) -> Material | None:
        return self.db.query(Material).filter(Material.id == material_id).first()

    def get_rock_materials(self, rock_id: str) -> List[Material]:
        return self.db.query(Material).filter(Material.rock_id == rock_id).all()

    def update_status(self, material_id: str, status: str, failure_reason: str = None) -> Material:
        material = self.get_by_id(material_id)
        if material:
            material.processing_status = status
            if failure_reason:
                material.failure_reason = failure_reason
            self.db.commit()
            self.db.refresh(material)
        return material
