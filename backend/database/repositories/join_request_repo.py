from sqlalchemy.orm import Session
from backend.models.join_request import JoinRequest
from typing import List

class JoinRequestRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, den_id: str, user_id: str) -> JoinRequest:
        req = JoinRequest(den_id=den_id, user_id=user_id)
        self.db.add(req)
        self.db.commit()
        self.db.refresh(req)
        return req

    def get_by_id(self, req_id: str) -> JoinRequest | None:
        return self.db.query(JoinRequest).filter(JoinRequest.id == req_id).first()
        
    def get_user_request(self, den_id: str, user_id: str) -> JoinRequest | None:
        return self.db.query(JoinRequest).filter(
            JoinRequest.den_id == den_id,
            JoinRequest.user_id == user_id,
            JoinRequest.status == "PENDING"
        ).first()

    def get_den_pending_requests(self, den_id: str) -> List[JoinRequest]:
        return self.db.query(JoinRequest).filter(
            JoinRequest.den_id == den_id, 
            JoinRequest.status == "PENDING"
        ).all()

    def update_status(self, req_id: str, status: str):
        req = self.get_by_id(req_id)
        if req:
            req.status = status
            self.db.commit()
            self.db.refresh(req)
        return req
