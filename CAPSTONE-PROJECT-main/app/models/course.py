from sqlalchemy import Boolean, Column, Integer, String
from sqlalchemy.orm import relationship
from app.db.session import Base


class Course(Base):
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    code = Column(String(50), unique=True, index=True, nullable=False)
    capacity = Column(Integer, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

    enrollments = relationship("Enrollment", back_populates="course", cascade="all, delete-orphan")