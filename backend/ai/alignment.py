from pydantic import BaseModel, Field
from typing import List, Optional
from backend.ai.gemini_client import GeminiClient

class AlignmentRelation(BaseModel):
    source_evidence_id: str
    target_evidence_id: str
    relationship: str = Field(description="Must be SUPPORTS, ELABORATES, REFERS_TO, AGREES_WITH, CONTRADICTS, CORRECTS, or UNCERTAIN_RELATIONSHIP")
    confidence: str = Field(description="Must be HIGH, MEDIUM, LOW, or UNKNOWN")
    reasoning: str = Field(description="Explanation of why this relationship exists")

class AlignmentResult(BaseModel):
    relations: List[AlignmentRelation]

class AlignmentService:
    def __init__(self):
        self.client = GeminiClient()

    def align_evidence(self, evidence_list: list) -> AlignmentResult:
        if len(evidence_list) < 2:
            return AlignmentResult(relations=[])
            
        system_instruction = (
            "You are an alignment engine for educational multimodal content. "
            "Given a list of extracted evidence from a lecture (audio, slides, notes), "
            "identify meaningful relationships between them. "
            "CRITICAL: You MUST aggressively check for factual contradictions (e.g. an incorrect formula like 'E = mc' compared to a correct one 'E = mc^2'). "
            "If you spot ANY conflicting data, you MUST create a 'CONTRADICTS' relationship between them. "
            "Output relationships like SUPPORTS, CONTRADICTS, CORRECTS. "
        )
        
        # Serialize evidence_list to JSON string for prompt
        import json
        evidence_json = json.dumps([
            {
                "id": e.id,
                "modality": e.modality,
                "content": e.content,
                "content_type": e.content_type
            } for e in evidence_list
        ], indent=2)
        
        prompt = f"Here is the list of evidence items. Find the relationships between them:\n\n{evidence_json}"
        
        result = self.client.generate_structured_content(
            prompt=prompt,
            response_schema=AlignmentResult,
            system_instruction=system_instruction
        )
        return result
