from sqlalchemy.orm import Session
from backend.models.qa import QAThread, QAMessage
from backend.models.fusion import FusedConcept
from backend.ai.gemini_client import GeminiClient
from backend.schemas.auth import UserResponse
from pydantic import BaseModel

class QAService:
    def __init__(self, db: Session):
        self.db = db
        self.client = GeminiClient()

    def get_den_threads(self, den_id: str):
        return self.db.query(QAThread).filter(QAThread.den_id == den_id).order_by(QAThread.created_at.desc()).all()

    def get_thread_messages(self, thread_id: str):
        return self.db.query(QAMessage).filter(QAMessage.thread_id == thread_id).order_by(QAMessage.created_at.asc()).all()

    def post_question(self, den_id: str, user: UserResponse, question_text: str):
        # 1. Create thread
        thread = QAThread(
            den_id=den_id,
            author_id=user.id,
            question=question_text
        )
        self.db.add(thread)
        self.db.commit()
        self.db.refresh(thread)

        # 2. Add user message
        user_msg = QAMessage(
            thread_id=thread.id,
            author_id=user.id,
            content=question_text,
            is_ai="false"
        )
        self.db.add(user_msg)
        self.db.commit()
        
        # 3. Enqueue job or call Gemini synchronously for this phase
        # We will do it synchronously for immediate feedback
        
        # Gather context (Concepts)
        concepts = self.db.query(FusedConcept).filter(FusedConcept.den_id == den_id).all()
        context_str = "\n".join([f"- {c.title}: {c.explanation}" for c in concepts])
        
        system_instruction = (
            "You are Syntra V2's teaching assistant. "
            "First, try to answer the student's question based strictly on the provided context concepts. "
            "If the context contains the answer, provide an evidence-backed explanation. "
            "If the context doesn't contain the answer, you MUST explicitly start your answer by saying 'Materials doesn't provide this question's concept.' and then proceed to answer the question generally using your own knowledge."
        )
        prompt = f"Context:\n{context_str}\n\nStudent Question: {question_text}"
        
        class QAAnswer(BaseModel):
            answer: str
            
        try:
            result = self.client.generate_structured_content(
                prompt=prompt,
                response_schema=QAAnswer,
                system_instruction=system_instruction
            )
            ai_content = result.answer
        except Exception:
            ai_content = "I'm sorry, I am currently unable to process your question. Please ensure API keys are configured."
            
        # 4. Add AI message
        ai_msg = QAMessage(
            thread_id=thread.id,
            author_id=None,
            content=ai_content,
            is_ai="true"
        )
        self.db.add(ai_msg)
        self.db.commit()
