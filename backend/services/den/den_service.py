from sqlalchemy.orm import Session
from backend.database.repositories.den_repo import DenRepository
from backend.database.repositories.membership_repo import MembershipRepository
from backend.database.repositories.join_request_repo import JoinRequestRepository
from backend.database.repositories.user_repo import UserRepository
from backend.models.membership import RoleEnum
from backend.models.ban import Ban
from backend.schemas.den import DenCreate, DenResponse, JoinRequestResponse
from backend.schemas.auth import UserResponse
from typing import List, Dict

class DenServiceError(Exception):
    pass

class DenService:
    def __init__(self, db: Session):
        self.db = db
        self.den_repo = DenRepository(db)
        self.membership_repo = MembershipRepository(db)
        self.join_request_repo = JoinRequestRepository(db)
        self.user_repo = UserRepository(db)

    def create_den(self, data: DenCreate, creator: UserResponse) -> DenResponse:
        den = self.den_repo.create(data)
        
        self.membership_repo.add_member(
            user_id=creator.id,
            den_id=den.id,
            role=RoleEnum.ADMIN
        )
        
        return DenResponse.model_validate(den)

    def get_user_dens(self, user: UserResponse) -> List[Dict]:
        memberships = self.membership_repo.get_user_dens(user.id)
        result = []
        for m in memberships:
            den = self.den_repo.get_by_id(m.den_id)
            if den:
                result.append({
                    "den": DenResponse.model_validate(den),
                    "role": m.role
                })
        return result

    def get_den(self, den_id: str, user: UserResponse) -> DenResponse:
        membership = self.membership_repo.get_membership(user.id, den_id)
        if not membership:
            raise DenServiceError("You are not a member of this Den.")
        
        den = self.den_repo.get_by_id(den_id)
        if not den:
            raise DenServiceError("Den not found.")
            
        return DenResponse.model_validate(den)

    def is_admin(self, den_id: str, user: UserResponse) -> bool:
        membership = self.membership_repo.get_membership(user.id, den_id)
        return membership is not None and membership.role == RoleEnum.ADMIN.value
        
    def _check_max_members(self, den_id: str):
        den = self.den_repo.get_by_id(den_id)
        if den and den.max_members is not None:
            members = self.membership_repo.get_den_members(den_id)
            if len(members) >= den.max_members:
                raise DenServiceError("This Den has reached its maximum member limit.")

    def _check_ban(self, den_id: str, user_id: str):
        ban = self.db.query(Ban).filter(Ban.den_id == den_id, Ban.user_id == user_id).first()
        if ban:
            raise DenServiceError("You are banned from this Den.")

    def request_to_join_den(self, den_id: str, user: UserResponse):
        den = self.den_repo.get_by_id(den_id)
        if not den:
            raise DenServiceError("Den not found.")
            
        if den.is_public == "false":
            raise DenServiceError("Cannot request to join a private Den.")
            
        self._check_ban(den_id, user.id)
            
        existing_member = self.membership_repo.get_membership(user.id, den_id)
        if existing_member:
            raise DenServiceError("You are already a member.")
            
        existing_req = self.join_request_repo.get_user_request(den_id, user.id)
        if existing_req:
            raise DenServiceError("You already have a pending join request.")
            
        self._check_max_members(den_id)
        self.join_request_repo.create(den_id, user.id)

    def join_den_with_code(self, den_id: str, code: str, user: UserResponse):
        den = self.den_repo.get_by_id(den_id)
        if not den:
            raise DenServiceError("Den not found.")
            
        if den.is_public == "true":
            raise DenServiceError("This is a public Den. Please request to join.")
            
        if den.invite_code != code:
            raise DenServiceError("Invalid invite code.")
            
        self._check_ban(den_id, user.id)
            
        existing_member = self.membership_repo.get_membership(user.id, den_id)
        if existing_member:
            raise DenServiceError("You are already a member.")
            
        self._check_max_members(den_id)
        self.membership_repo.add_member(user.id, den_id, RoleEnum.MEMBER)
        
    def get_join_requests(self, den_id: str, user: UserResponse) -> List[JoinRequestResponse]:
        if not self.is_admin(den_id, user):
            raise DenServiceError("Only Admins can view join requests.")
        requests = self.join_request_repo.get_den_pending_requests(den_id)
        return [JoinRequestResponse.model_validate(req) for req in requests]
        
    def resolve_join_request(self, req_id: str, approve: bool, user: UserResponse):
        req = self.join_request_repo.get_by_id(req_id)
        if not req or req.status != "PENDING":
            raise DenServiceError("Join request not found or already resolved.")
            
        if not self.is_admin(req.den_id, user):
            raise DenServiceError("Only Admins can resolve join requests.")
            
        if approve:
            self._check_max_members(req.den_id)
            self.join_request_repo.update_status(req_id, "APPROVED")
            self.membership_repo.add_member(req.user_id, req.den_id, RoleEnum.MEMBER)
        else:
            self.join_request_repo.update_status(req_id, "REJECTED")

    def leave_den(self, den_id: str, user: UserResponse):
        membership = self.membership_repo.get_membership(user.id, den_id)
        if not membership:
            raise DenServiceError("You are not a member of this Den.")
            
        if membership.role == RoleEnum.ADMIN.value:
            admins = [m for m in self.membership_repo.get_den_members(den_id) if m.role == RoleEnum.ADMIN.value]
            if len(admins) == 1:
                raise DenServiceError("You are the last admin. Delete the Den instead of leaving.")
                
        self.membership_repo.remove_member(user.id, den_id)
        
    def delete_den(self, den_id: str, user: UserResponse):
        if not self.is_admin(den_id, user):
            raise DenServiceError("Only Admins can delete a Den.")
        self.den_repo.delete(den_id)

    def get_members_with_info(self, den_id: str) -> List[Dict]:
        members = self.membership_repo.get_den_members(den_id)
        res = []
        for m in members:
            u = self.user_repo.get_by_id(m.user_id)
            if u:
                res.append({
                    "user_id": u.id,
                    "display_name": u.display_name,
                    "email": u.email,
                    "role": m.role
                })
        return res
        
    def remove_member(self, den_id: str, target_user_id: str, user: UserResponse):
        if not self.is_admin(den_id, user):
            raise DenServiceError("Only Admins can remove members.")
            
        if target_user_id == user.id:
            raise DenServiceError("You cannot remove yourself. Use 'Leave Den'.")
            
        self.membership_repo.remove_member(target_user_id, den_id)
        
    def ban_member(self, den_id: str, target_user_id: str, user: UserResponse):
        if not self.is_admin(den_id, user):
            raise DenServiceError("Only Admins can ban members.")
            
        if target_user_id == user.id:
            raise DenServiceError("You cannot ban yourself.")
            
        # Remove from den
        self.membership_repo.remove_member(target_user_id, den_id)
        
        # Add to bans
        existing_ban = self.db.query(Ban).filter(Ban.den_id == den_id, Ban.user_id == target_user_id).first()
        if not existing_ban:
            ban = Ban(den_id=den_id, user_id=target_user_id)
            self.db.add(ban)
            self.db.commit()
