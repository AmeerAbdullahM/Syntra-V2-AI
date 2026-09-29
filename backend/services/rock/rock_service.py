from sqlalchemy.orm import Session
from backend.database.repositories.rock_repo import RockRepository
from backend.services.den.den_service import DenService
from backend.schemas.rock import RockCreate, RockResponse
from backend.schemas.auth import UserResponse
from typing import List

class RockServiceError(Exception):
    pass

class RockService:
    def __init__(self, db: Session):
        self.db = db
        self.rock_repo = RockRepository(db)
        self.den_service = DenService(db)

    def create_rock(self, data: RockCreate, user: UserResponse) -> RockResponse:
        if not self.den_service.is_admin(data.den_id, user):
            raise RockServiceError("Only Den admins can create Rocks.")
        
        rock = self.rock_repo.create(data)
        return RockResponse.model_validate(rock)

    def get_den_rocks(self, den_id: str, user: UserResponse) -> List[RockResponse]:
        # User must be at least a member
        self.den_service.get_den(den_id, user) 
        rocks = self.rock_repo.get_den_rocks(den_id)
        return [RockResponse.model_validate(r) for r in rocks]

    def trigger_fusion(self, rock_id: str, user: UserResponse):
        rock = self.rock_repo.get_by_id(rock_id)
        if not rock:
            raise RockServiceError("Rock not found")
        if not self.den_service.is_admin(rock.den_id, user):
            raise RockServiceError("Only Den admins can trigger fusion.")
            
        from backend.queue.postgres_queue import PostgresQueue
        from backend.models.job import JobTypeEnum
        
        queue = PostgresQueue(self.db)
        queue.enqueue(
            job_type=JobTypeEnum.ROCK_FUSION.value,
            den_id=rock.den_id,
            target_id=rock.id,
            user_id=user.id,
            payload={"rock_id": rock.id}
        )

    def delete_rock(self, rock_id: str, user: UserResponse):
        rock = self.rock_repo.get_by_id(rock_id)
        if not rock:
            raise RockServiceError("Rock not found")
        if not self.den_service.is_admin(rock.den_id, user):
            raise RockServiceError("Only Den admins can delete Rocks.")
            
        from backend.storage.factory import get_storage
        from backend.database.repositories.material_repo import MaterialRepository
        storage = get_storage()
        mat_repo = MaterialRepository(self.db)
        materials = mat_repo.get_rock_materials(rock.id)
        
        for mat in materials:
            try:
                storage.delete(mat.stored_filename)
            except Exception:
                pass
                
        self.rock_repo.delete(rock.id)
