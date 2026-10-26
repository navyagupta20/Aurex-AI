
import os
import json
from datetime import datetime

from dotenv import load_dotenv
from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    Text,
    DateTime,
    Float,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base, sessionmaker

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError(
        "DATABASE_URL is missing. Please check your .env file."
    )

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False)
Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=False), primary_key=True)
    full_name = Column("name", String(100), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)


class PracticeSession(Base):
    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True, index=True)
    student_name = Column(String(100), nullable=False)
    mode = Column(String(50), nullable=False)
    topic = Column(String(300), nullable=False)
    score = Column(Float, nullable=False, default=0)
    scores_json = Column(Text, nullable=False, default="{}")
    feedback = Column(Text, nullable=False, default="")
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)


def initialize_database():
    # Existing tables are preserved. This creates missing mapped tables only.
    Base.metadata.create_all(bind=engine)


def create_user(full_name, email, password_hash):
    from uuid import uuid4

    db = SessionLocal()
    try:
        user = User(
            id=str(uuid4()),
            full_name=full_name.strip(),
            email=email.strip().lower(),
            password_hash=password_hash,
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        return {
            "id": str(user.id),
            "full_name": user.full_name,
            "email": user.email,
            "password_hash": user.password_hash,
        }
    except Exception as error:
        db.rollback()

        if "unique" in str(error).lower():
            return None

        raise
    finally:
        db.close()


def get_user_by_email(email):
    db = SessionLocal()
    try:
        user = (
            db.query(User)
            .filter(User.email == email.strip().lower())
            .first()
        )

        if user is None:
            return None

        return {
            "id": str(user.id),
            "full_name": user.full_name,
            "email": user.email,
            "password_hash": user.password_hash,
        }
    finally:
        db.close()


def save_session(
    student_name,
    mode,
    topic,
    score,
    scores,
    feedback,
):
    db = SessionLocal()
    try:
        if not isinstance(scores, str):
            scores = json.dumps(scores)

        record = PracticeSession(
            student_name=student_name,
            mode=mode,
            topic=topic,
            score=float(score or 0),
            scores_json=scores,
            feedback=feedback or "",
        )
        db.add(record)
        db.commit()
        db.refresh(record)
        return record.id
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def _to_dict(record):
    return {
        "id": record.id,
        "student_name": record.student_name,
        "mode": record.mode,
        "topic": record.topic,
        "score": record.score,
        "scores": record.scores_json,
        "feedback": record.feedback,
        "created_at": record.created_at,
    }


def get_sessions(student_name="Student", limit=None):
    db = SessionLocal()
    try:
        query = (
            db.query(PracticeSession)
            .filter(PracticeSession.student_name == student_name)
            .order_by(PracticeSession.created_at.desc())
        )

        if limit is not None:
            query = query.limit(limit)

        return [_to_dict(record) for record in query.all()]
    finally:
        db.close()


def get_session_by_id(session_id):
    db = SessionLocal()
    try:
        record = (
            db.query(PracticeSession)
            .filter(PracticeSession.id == session_id)
            .first()
        )
        return _to_dict(record) if record else None
    finally:
        db.close()


def delete_all_sessions():
    db = SessionLocal()
    try:
        db.query(PracticeSession).delete()
        db.commit()
    finally:
        db.close()


initialize_database()
