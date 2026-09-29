from pydantic import BaseModel, Field
from typing import List, Optional
from backend.ai.gemini_client import GeminiClient

class FusedConceptItem(BaseModel):
    title: str = Field(description="Name of the concept")
    explanation: str = Field(description="Synthesized explanation based on evidence")
    confidence: str = Field(description="HIGH, MEDIUM, LOW")
    alignment_status: str = Field(description="ALIGNED, UNRESOLVED_CONFLICT, EXPLICIT_CORRECTION, INSUFFICIENT_EVIDENCE")
    evidence_ids: List[str] = Field(description="List of evidence IDs used to form this concept")
    accessibility_description: Optional[str] = Field(None, description="Accessible description for screen readers/alt text")

class FusedConceptList(BaseModel):
    concepts: List[FusedConceptItem]

class FusionService:
    def __init__(self):
        self.client = GeminiClient()

    def fuse_evidence(self, evidence_list: list, relations_list: list) -> FusedConceptList:
        if not evidence_list:
            return FusedConceptList(concepts=[])
            
        system_instruction = (
            "You are a fusion engine for educational multimodal content. "
            "Given a list of extracted evidence and their relationships, synthesize the core concepts. "
            "If there are contradictions, note them and set alignment_status to UNRESOLVED_CONFLICT or EXPLICIT_CORRECTION. "
            "Every factual claim MUST trace back to the provided evidence. "
            "Do NOT invent general knowledge."
        )
        
        import json
        context = {
            "evidence": [
                {
                    "id": e.id,
                    "content": e.content,
                    "modality": e.modality
                } for e in evidence_list
            ],
            "relations": [
                {
                    "source": r.source_evidence_id,
                    "target": r.target_evidence_id,
                    "relationship": r.relationship,
                    "reasoning": r.reasoning
                } for r in relations_list
            ]
        }
        
        prompt = f"Please fuse the following evidence into distinct concepts:\n\n{json.dumps(context, indent=2)}"
        
        result = self.client.generate_structured_content(
            prompt=prompt,
            response_schema=FusedConceptList,
            system_instruction=system_instruction
        )
        return result
