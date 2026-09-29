from pydantic import BaseModel, Field
from typing import List, Optional
from backend.ai.gemini_client import GeminiClient, GeminiClientError

class ExtractedEvidenceItem(BaseModel):
    content: str = Field(description="The extracted content (e.g. transcript segment, diagram label, equation)")
    content_type: str = Field(description="Type of content: 'transcript', 'equation', 'diagram_label', 'heading', 'handwritten_note', 'visual_observation'")
    confidence: str = Field(description="Must be HIGH, MEDIUM, LOW, or UNKNOWN")
    start_time: Optional[str] = Field(None, description="Start time if audio (e.g. '00:32')")
    end_time: Optional[str] = Field(None, description="End time if audio (e.g. '00:48')")
    page_number: Optional[int] = Field(None, description="Page number if document/slide")
    region: Optional[str] = Field(None, description="Description of the visual region if image")

class ExtractedEvidenceList(BaseModel):
    items: List[ExtractedEvidenceItem]

class ExtractionService:
    def __init__(self):
        self.client = GeminiClient()

    def extract_evidence(self, file_path: str, mime_type: str, modality: str) -> ExtractedEvidenceList:
        gemini_file = None
        try:
            gemini_file = self.client.upload_file(file_path, mime_type)
            
            system_instruction = (
                "You are an evidence extraction engine for an educational system. "
                "Extract structured evidence from the provided material. "
                "Do NOT simply summarize. Extract specific claims, transcript segments, equations, or visual labels. "
                "When determining 'confidence', you MUST evaluate the factual accuracy of the extracted statement. "
                "If a claim or equation is factually incorrect or missing critical context (e.g., E = mc instead of E = mc^2), mark confidence as LOW. "
                "If something is blurry or ambiguous in the source, also mark confidence as LOW. "
                "Do NOT invent missing timestamps or hallucinate text."
            )
            
            prompt = f"Please extract evidence from this {modality} material."
            
            result = self.client.generate_structured_content(
                prompt=prompt,
                response_schema=ExtractedEvidenceList,
                system_instruction=system_instruction,
                files=[gemini_file]
            )
            return result
        finally:
            if gemini_file:
                # Cleanup file from Gemini API to save quota
                try:
                    self.client.client.files.delete(name=gemini_file.name)
                except:
                    pass
