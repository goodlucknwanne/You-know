from sqlalchemy import Boolean, Column, Enum, Integer, String
from sqlalchemy.orm import relationship
from app.db.session import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(Enum("student", "admin", name="user_role"), nullable=False, default="student")
    is_active = Column(Boolean, default=True, nullable=False)

    enrollments = relationship("Enrollment", back_populates="user", cascade="all, delete-orphan")