from sqlalchemy.orm import Session
from backend.models.membership import Membership, RoleEnum
from typing import List

class MembershipRepository:
    def __init__(self, db: Session):
        self.db = db

    def add_member(self, user_id: str, den_id: str, role: RoleEnum = RoleEnum.MEMBER) -> Membership:
        membership = Membership(
            user_id=user_id,
            den_id=den_id,
            role=role.value
        )
        self.db.add(membership)
        self.db.commit()
        self.db.refresh(membership)
        return membership

    def get_user_dens(self, user_id: str) -> List[Membership]:
        return self.db.query(Membership).filter(Membership.user_id == user_id).all()

    def get_membership(self, user_id: str, den_id: str) -> Membership | None:
        return self.db.query(Membership).filter(
            Membership.user_id == user_id,
            Membership.den_id == den_id
        ).first()

    def get_den_members(self, den_id: str) -> List[Membership]:
        return self.db.query(Membership).filter(Membership.den_id == den_id).all()

    def remove_member(self, user_id: str, den_id: str):
        membership = self.get_membership(user_id, den_id)
        if membership:
            self.db.delete(membership)
            self.db.commit()
