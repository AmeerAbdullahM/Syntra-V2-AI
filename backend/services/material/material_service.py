import hashlib
import os
import uuid
from typing import BinaryIO
from sqlalchemy.orm import Session
from backend.database.repositories.material_repo import MaterialRepository
from backend.services.den.den_service import DenService
from backend.services.rock.rock_service import RockService
from backend.schemas.material import MaterialCreate, MaterialResponse
from backend.schemas.auth import UserResponse
from backend.storage.factory import get_storage
from backend.models.material import ModalityEnum

class MaterialServiceError(Exception):
    pass

class MaterialService:
    def __init__(self, db: Session):
        self.db = db
        self.material_repo = MaterialRepository(db)
        self.den_service = DenService(db)
        self.rock_service = RockService(db)
        self.storage = get_storage()

    def _determine_modality(self, mime_type: str) -> str:
        if mime_type.startswith("audio/"):
            return ModalityEnum.AUDIO.value
        elif mime_type.startswith("image/"):
            return ModalityEnum.VISUAL.value
        elif mime_type == "application/pdf":
            return ModalityEnum.DOCUMENT.value
        elif mime_type == "text/plain":
            return ModalityEnum.TEXT.value
        else:
            raise MaterialServiceError(f"Unsupported mime type: {mime_type}")

    def _compute_checksum(self, content: BinaryIO) -> str:
        sha256 = hashlib.sha256()
        content.seek(0)
        while chunk := content.read(8192):
            sha256.update(chunk)
        content.seek(0)
        return sha256.hexdigest()

    def upload_material(
        self, 
        den_id: str, 
        rock_id: str, 
        user: UserResponse, 
        filename: str, 
        mime_type: str, 
        content: BinaryIO, 
        size_bytes: int
    ) -> MaterialResponse:
        
        # Verify permissions: only admins can upload materials
        if not self.den_service.is_admin(den_id, user):
            raise MaterialServiceError("Only Den admins can upload materials directly. Members must submit an Add Request.")

        modality = self._determine_modality(mime_type)
        checksum = self._compute_checksum(content)

        # Generate unique storage filename
        stored_filename = f"{den_id}/{rock_id}/{uuid.uuid4()}_{filename}"
        
        # Save to storage
        try:
            self.storage.save(stored_filename, content)
        except Exception as e:
            raise MaterialServiceError(f"Failed to save file: {e}")

        # Create record
        create_data = MaterialCreate(
            den_id=den_id,
            rock_id=rock_id,
            uploader_id=user.id,
            original_filename=filename,
            stored_filename=stored_filename,
            mime_type=mime_type,
            size_bytes=size_bytes,
            checksum=checksum,
            modality=modality
        )
        
        from backend.queue.postgres_queue import PostgresQueue
        from backend.models.job import JobTypeEnum

        material = self.material_repo.create(create_data)
        
        # Enqueue processing job
        queue = PostgresQueue(self.db)
        queue.enqueue(
            job_type=JobTypeEnum.MATERIAL_PROCESS.value,
            den_id=den_id,
            target_id=material.id,
            user_id=user.id,
            payload={"material_id": material.id, "modality": modality}
        )
        
        # Update material status
        self.material_repo.update_status(material.id, "QUEUED")
        
        return MaterialResponse.model_validate(material)

    def get_rock_materials(self, rock_id: str, user: UserResponse) -> list[MaterialResponse]:
        # Validate rock exists and user has access to its den
        rock = self.rock_service.rock_repo.get_by_id(rock_id)
        if not rock:
            raise MaterialServiceError("Rock not found")
        self.den_service.get_den(rock.den_id, user)
        
        materials = self.material_repo.get_rock_materials(rock_id)
        return [MaterialResponse.model_validate(m) for m in materials]
