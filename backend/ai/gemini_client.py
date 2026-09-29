import os
from google import genai
from pydantic import BaseModel
from typing import Type, TypeVar, Any
from backend.config.settings import settings

T = TypeVar('T', bound=BaseModel)

class GeminiClientError(Exception):
    pass

class GeminiClient:
    def __init__(self):
        api_key = settings.GEMINI_API_KEY
        if not api_key:
            # We'll let it fail later or mock it for testing if empty
            pass
        self.client = genai.Client(api_key=api_key)
        self.model_id = "gemini-flash-lite-latest"

    def upload_file(self, file_path: str, mime_type: str):
        """Uploads a file to Gemini File API for processing."""
        try:
            return self.client.files.upload(path=file_path, config={'mime_type': mime_type})
        except Exception as e:
            raise GeminiClientError(f"Failed to upload file to Gemini: {e}")

    def generate_structured_content(self, prompt: str, response_schema: Type[T], system_instruction: str = None, files: list = None) -> T:
        """Generates structured content using Gemini."""
        try:
            contents = []
            if files:
                for f in files:
                    part = genai.types.Part.from_uri(file_uri=f.uri, mime_type=f.mime_type)
                    contents.append(part)
                
            schema_json = response_schema.model_json_schema()
            full_prompt = prompt + f"\n\nIMPORTANT: Return ONLY a valid JSON object. It MUST strictly conform to the following JSON schema:\n{schema_json}"
            contents.append(full_prompt)
            
            config = {
                "response_mime_type": "application/json",
                "temperature": 0.2
            }
            if system_instruction:
                config["system_instruction"] = system_instruction
                
            response = self.client.models.generate_content(
                model=self.model_id,
                contents=contents,
                config=config
            )
            
            return response_schema.model_validate_json(response.text)
            
        except Exception as e:
            raise GeminiClientError(f"Gemini generation failed: {e}")
