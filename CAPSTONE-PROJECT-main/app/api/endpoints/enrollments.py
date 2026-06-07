from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from api.deps import require_admin, require_student
from db.session import get_db
from schemas.enrollment import EnrollmentResponse, EnrollmentSimple
from services.enrollment_service import (
    admin_remove_student,
    deregister_student,
    enroll_student,
    get_all_enrollments,
    get_course_enrollments,
)

enrollment_router = APIRouter()


@enrollment_router.post("/{course_id}", response_model=EnrollmentSimple, status_code=201)
def enroll(
    course_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_student),
):
    """Enroll the authenticated student in a course."""
    return enroll_student(db, current_user, course_id)


@enrollment_router.delete("/{course_id}", status_code=204)
def deregister(
    course_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_student),
):
    """Deregister the authenticated student from a course."""
    deregister_student(db, current_user, course_id)


@enrollment_router.get("/", response_model=List[EnrollmentResponse])
def list_all_enrollments(
    db: Session = Depends(get_db),
    _=Depends(require_admin),
):
    """View all enrollments (admin only)."""
    return get_all_enrollments(db)


@enrollment_router.get("/course/{course_id}", response_model=List[EnrollmentResponse])
def list_course_enrollments(
    course_id: int,
    db: Session = Depends(get_db),
    _=Depends(require_admin),
):
    """View all enrollments for a specific course (admin only)."""
    return get_course_enrollments(db, course_id)


@enrollment_router.delete("/admin/{enrollment_id}", status_code=204)
def admin_remove(
    enrollment_id: int,
    db: Session = Depends(get_db),
    _=Depends(require_admin),
):
    """Remove a student from a course by enrollment ID (admin only)."""
    admin_remove_student(db, enrollment_id)