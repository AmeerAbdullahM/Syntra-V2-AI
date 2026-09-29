from sqlalchemy.orm import Session
from backend.models.artifact import Artifact
from backend.models.fusion import FusedConcept
from backend.models.evidence import Evidence
from backend.ai.gemini_client import GeminiClient
from backend.schemas.auth import UserResponse
from pydantic import BaseModel

class ArtifactService:
    def __init__(self, db: Session):
        self.db = db
        self.client = GeminiClient()

    def get_den_artifacts(self, den_id: str):
        return self.db.query(Artifact).filter(Artifact.den_id == den_id).all()

    def generate_cheat_sheet(self, den_id: str, rock_id: str, user: UserResponse) -> Artifact:
        concepts = self.db.query(FusedConcept).filter(FusedConcept.den_id == den_id).all()
        
        if not concepts:
            raise Exception("No fused concepts available to generate an artifact.")
            
        context_str = "\n\n".join([f"### {c.title}\n{c.explanation}" for c in concepts])
        
        system_instruction = (
            "You are an educational assistant. "
            "Generate a highly condensed, easy-to-read 'Cheat Sheet' based strictly on the provided concepts. "
            "Use markdown formatting with bolding, lists, and clear headings. "
            "Do NOT include conversational filler. Just the cheat sheet."
        )
        prompt = f"Please generate a Markdown cheat sheet for the following concepts:\n{context_str}"
        
        class ArtifactResult(BaseModel):
            title: str
            markdown_content: str
            
        try:
            result = self.client.generate_structured_content(
                prompt=prompt,
                response_schema=ArtifactResult,
                system_instruction=system_instruction
            )
            title = result.title
            content = result.markdown_content
        except Exception:
            title = "Generated Cheat Sheet"
            content = "Could not generate content. Please ensure API keys are configured."
            
        artifact = Artifact(
            den_id=den_id,
            rock_id=rock_id,
            title=title,
            artifact_type="CHEAT_SHEET",
            content_markdown=content
        )
        self.db.add(artifact)
        self.db.commit()
        self.db.refresh(artifact)
        return artifact
