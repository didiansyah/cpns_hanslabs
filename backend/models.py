from sqlalchemy import Column, Integer, String, Boolean, DateTime, Date, Text, DECIMAL, JSON, ForeignKey, UniqueConstraint
from sqlalchemy.sql import func
from db import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=True)
    phone = Column(String(20))
    education = Column(String(50))
    target_instansi = Column(String(100))
    previous_cpns = Column(Boolean, default=False)
    verified = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

class EmailOTP(Base):
    __tablename__ = "email_otps"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer)
    email = Column(String(100), nullable=False, index=True)
    code = Column(String(6), nullable=False)
    expires_at = Column(DateTime, nullable=False)
    attempts = Column(Integer, default=0)
    used = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())

class PasswordResetToken(Base):
    __tablename__ = "password_reset_tokens"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    email = Column(String(100), nullable=False, index=True)
    token_hash = Column(String(64), nullable=False, unique=True)
    expires_at = Column(DateTime, nullable=False)
    attempts = Column(Integer, default=0)
    used = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())

class Progress(Base):
    __tablename__ = "progress"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    study_days = Column(Integer, default=0)
    study_hours = Column(DECIMAL(10, 2), default=0)
    sim_count = Column(Integer, default=0)
    current_week = Column(Integer, default=1)
    twk_score = Column(DECIMAL(5, 2), default=0)
    tiu_score = Column(DECIMAL(5, 2), default=0)
    tkp_score = Column(DECIMAL(5, 2), default=0)
    streak_days = Column(Integer, default=0)
    last_study_date = Column(Date)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

class Simulation(Base):
    __tablename__ = "simulations"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    sim_type = Column(String(20), nullable=False)
    package_id = Column(Integer, ForeignKey("tryout_packages.id"), nullable=True, index=True)
    twk_score = Column(Integer)
    tiu_score = Column(Integer)
    tkp_score = Column(Integer)
    total_score = Column(Integer)
    passed = Column(Boolean)
    duration_seconds = Column(Integer)
    questions_data = Column(JSON)
    submitted_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, server_default=func.now())

class TryoutPackage(Base):
    __tablename__ = "tryout_packages"
    id = Column(Integer, primary_key=True, autoincrement=True)
    part_number = Column(Integer, nullable=False, unique=True)
    title = Column(String(120), nullable=False)
    sim_type = Column(String(20), default="full", nullable=False)
    question_ids = Column(JSON, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, server_default=func.now())

class Question(Base):
    __tablename__ = "questions"
    id = Column(Integer, primary_key=True, autoincrement=True)
    section = Column(String(3), nullable=False, index=True)
    topic = Column(String(100), nullable=False, index=True)
    year = Column(Integer)
    difficulty = Column(String(20))
    question_text = Column(Text, nullable=False)
    options = Column(JSON, nullable=False)
    correct_answer = Column(Integer)
    explanation = Column(Text)
    created_at = Column(DateTime, server_default=func.now())

class Checklist(Base):
    __tablename__ = "checklists"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    date = Column(Date, nullable=False)
    chk1 = Column(Boolean, default=False)
    chk2 = Column(Boolean, default=False)
    chk3 = Column(Boolean, default=False)
    chk4 = Column(Boolean, default=False)
    chk5 = Column(Boolean, default=False)
    __table_args__ = (UniqueConstraint("user_id", "date", name="uniq_user_date"),)

class StudyLog(Base):
    __tablename__ = "study_logs"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    duration_minutes = Column(Integer, nullable=False)
    topic = Column(String(100))
    section = Column(String(3))
    notes = Column(Text)
    created_at = Column(DateTime, server_default=func.now())
