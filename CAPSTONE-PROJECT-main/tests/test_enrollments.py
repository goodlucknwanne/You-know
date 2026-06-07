import pytest
from tests.conftest import auth_headers, create_course_as_admin, register_and_login


@pytest.fixture
def admin_token(client):
    return register_and_login(client, "admin@test.com", "admin1234", "admin", "Admin")


@pytest.fixture
def student_token(client):
    return register_and_login(client, "student@test.com", "student123", "student", "Student")


@pytest.fixture
def student2_token(client):
    return register_and_login(client, "student2@test.com", "student123", "student", "Student2")


@pytest.fixture
def active_course(client, admin_token):
    return create_course_as_admin(client, admin_token, title="Math 101", code="MATH101", capacity=5)


@pytest.fixture
def inactive_course(client, admin_token):
    c = create_course_as_admin(client, admin_token, title="Dead Course", code="DEAD1", capacity=10)
    client.put(f"/api/v1/courses/{c['id']}", json={"is_active": False}, headers=auth_headers(admin_token))
    return c


class TestEnroll:
    def test_student_can_enroll(self, client, student_token, active_course):
        resp = client.post(
            f"/api/v1/enrollments/{active_course['id']}",
            headers=auth_headers(student_token),
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["course_id"] == active_course["id"]

    def test_admin_cannot_enroll(self, client, admin_token, active_course):
        resp = client.post(
            f"/api/v1/enrollments/{active_course['id']}",
            headers=auth_headers(admin_token),
        )
        assert resp.status_code == 403

    def test_unauthenticated_cannot_enroll(self, client, active_course):
        resp = client.post(f"/api/v1/enrollments/{active_course['id']}")
        assert resp.status_code == 401

    def test_cannot_enroll_twice(self, client, student_token, active_course):
        client.post(f"/api/v1/enrollments/{active_course['id']}", headers=auth_headers(student_token))
        resp = client.post(f"/api/v1/enrollments/{active_course['id']}", headers=auth_headers(student_token))
        assert resp.status_code == 409

    def test_cannot_enroll_inactive_course(self, client, student_token, inactive_course):
        resp = client.post(
            f"/api/v1/enrollments/{inactive_course['id']}",
            headers=auth_headers(student_token),
        )
        assert resp.status_code == 400
        assert "inactive" in resp.json()["detail"].lower()

    def test_cannot_enroll_nonexistent_course(self, client, student_token):
        resp = client.post("/api/v1/enrollments/9999", headers=auth_headers(student_token))
        assert resp.status_code == 404

    def test_enrollment_fails_when_course_full(self, client, admin_token):
        # Create a course with capacity 1
        tiny = create_course_as_admin(client, admin_token, code="TINY1", capacity=1)

        # First student enrolls successfully
        t1 = register_and_login(client, "s1@test.com", "pass1234", "student", "S1")
        r1 = client.post(f"/api/v1/enrollments/{tiny['id']}", headers=auth_headers(t1))
        assert r1.status_code == 201

        # Second student is rejected
        t2 = register_and_login(client, "s2@test.com", "pass1234", "student", "S2")
        r2 = client.post(f"/api/v1/enrollments/{tiny['id']}", headers=auth_headers(t2))
        assert r2.status_code == 400
        assert "full" in r2.json()["detail"].lower()


class TestDeregister:
    def test_student_can_deregister(self, client, student_token, active_course):
        client.post(f"/api/v1/enrollments/{active_course['id']}", headers=auth_headers(student_token))
        resp = client.delete(
            f"/api/v1/enrollments/{active_course['id']}",
            headers=auth_headers(student_token),
        )
        assert resp.status_code == 204

    def test_deregister_not_enrolled(self, client, student_token, active_course):
        resp = client.delete(
            f"/api/v1/enrollments/{active_course['id']}",
            headers=auth_headers(student_token),
        )
        assert resp.status_code == 404

    def test_student_cannot_deregister_others(self, client, student_token, student2_token, active_course):
        # student2 enrolls
        client.post(f"/api/v1/enrollments/{active_course['id']}", headers=auth_headers(student2_token))
        # student tries to deregister student2's enrollment (their own — not enrolled)
        resp = client.delete(
            f"/api/v1/enrollments/{active_course['id']}",
            headers=auth_headers(student_token),
        )
        assert resp.status_code == 404

    def test_can_re_enroll_after_deregistering(self, client, student_token, active_course):
        client.post(f"/api/v1/enrollments/{active_course['id']}", headers=auth_headers(student_token))
        client.delete(f"/api/v1/enrollments/{active_course['id']}", headers=auth_headers(student_token))
        resp = client.post(f"/api/v1/enrollments/{active_course['id']}", headers=auth_headers(student_token))
        assert resp.status_code == 201


class TestAdminEnrollmentViews:
    def test_admin_can_list_all_enrollments(self, client, admin_token, student_token, active_course):
        client.post(f"/api/v1/enrollments/{active_course['id']}", headers=auth_headers(student_token))
        resp = client.get("/api/v1/enrollments/", headers=auth_headers(admin_token))
        assert resp.status_code == 200
        assert len(resp.json()) >= 1

    def test_student_cannot_list_all_enrollments(self, client, student_token):
        resp = client.get("/api/v1/enrollments/", headers=auth_headers(student_token))
        assert resp.status_code == 403

    def test_admin_can_list_course_enrollments(self, client, admin_token, student_token, active_course):
        client.post(f"/api/v1/enrollments/{active_course['id']}", headers=auth_headers(student_token))
        resp = client.get(
            f"/api/v1/enrollments/course/{active_course['id']}",
            headers=auth_headers(admin_token),
        )
        assert resp.status_code == 200
        assert all(e["course_id"] == active_course["id"] for e in resp.json())

    def test_list_course_enrollments_nonexistent_course(self, client, admin_token):
        resp = client.get("/api/v1/enrollments/course/9999", headers=auth_headers(admin_token))
        assert resp.status_code == 404

    def test_admin_can_remove_enrollment(self, client, admin_token, student_token, active_course):
        client.post(f"/api/v1/enrollments/{active_course['id']}", headers=auth_headers(student_token))
        enrollments = client.get("/api/v1/enrollments/", headers=auth_headers(admin_token)).json()
        enrollment_id = enrollments[0]["id"]

        resp = client.delete(
            f"/api/v1/enrollments/admin/{enrollment_id}",
            headers=auth_headers(admin_token),
        )
        assert resp.status_code == 204

        # Verify removed
        remaining = client.get("/api/v1/enrollments/", headers=auth_headers(admin_token)).json()
        assert all(e["id"] != enrollment_id for e in remaining)

    def test_admin_remove_nonexistent_enrollment(self, client, admin_token):
        resp = client.delete("/api/v1/enrollments/admin/9999", headers=auth_headers(admin_token))
        assert resp.status_code == 404

    def test_student_cannot_admin_remove(self, client, student_token):
        resp = client.delete("/api/v1/enrollments/admin/1", headers=auth_headers(student_token))
        assert resp.status_code == 403