from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime, timezone

from app.database import get_db
from app.models.models import User, QuizProfile
from app.schemas.schemas import QuizUpdate, QuizOut
from app.core.deps import get_current_user

router = APIRouter()


@router.post("", response_model=QuizOut)
def save_quiz(
    data: QuizUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Save or update user's context questionnaire responses."""
    quiz = db.query(QuizProfile).filter(QuizProfile.user_id == current_user.id).first()
    if not quiz:
        quiz = QuizProfile(
            user_id=current_user.id,
            q_rel=data.q_rel,
            q_job=data.q_job,
            q_focus=data.q_focus,
            completed_at=datetime.now(timezone.utc)
        )
        db.add(quiz)
    else:
        if data.q_rel is not None:
            quiz.q_rel = data.q_rel
        if data.q_job is not None:
            quiz.q_job = data.q_job
        if data.q_focus is not None:
            quiz.q_focus = data.q_focus
        quiz.completed_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(quiz)
    return quiz


@router.get("", response_model=QuizOut)
def get_quiz(
    current_user: User = Depends(get_current_user)
):
    """Get user's questionnaire responses."""
    if not current_user.quiz:
        return QuizOut()
    return current_user.quiz
