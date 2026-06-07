from typing import List
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.models.enrollment import Enrollment
from app.models.course import Course
from app.models.user import User
from app.services.course_service import get_course_by_id


def enroll_student(db: Session, user: User, course_id: int) -> Enrollment:
    course = get_course_by_id(db, course_id)

    if not course.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot enroll in an inactive course",
        )

    existing = (
        db.query(Enrollment)
        .filter(Enrollment.user_id == user.id, Enrollment.course_id == course_id)
        .first()
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Already enrolled in this course",
        )

    enrolled_count = db.query(Enrollment).filter(Enrollment.course_id == course_id).count()
    if enrolled_count >= course.capacity:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Course is full",
        )

    enrollment = Enrollment(user_id=user.id, course_id=course_id)
    db.add(enrollment)
    db.commit()
    db.refresh(enrollment)
    return enrollment


def deregister_student(db: Session, user: User, course_id: int) -> None:
    enrollment = (
        db.query(Enrollment)
        .filter(Enrollment.user_id == user.id, Enrollment.course_id == course_id)
        .first()
    )
    if not enrollment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Enrollment not found",
        )
    db.delete(enrollment)
    db.commit()


def get_all_enrollments(db: Session) -> List[Enrollment]:
    return db.query(Enrollment).all()


def get_course_enrollments(db: Session, course_id: int) -> List[Enrollment]:
    get_course_by_id(db, course_id)
    return db.query(Enrollment).filter(Enrollment.course_id == course_id).all()


def admin_remove_student(db: Session, enrollment_id: int) -> None:
    enrollment = db.query(Enrollment).filter(Enrollment.id == enrollment_id).first()
    if not enrollment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Enrollment not found",
        )
    db.delete(enrollment)
    db.commit()