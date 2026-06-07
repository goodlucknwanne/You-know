import pytest
from tests.conftest import auth_headers, create_course_as_admin, register_and_login


@pytest.fixture
def admin_token(client):
    return register_and_login(client, "admin@test.com", "admin1234", "admin", "Admin User")


@pytest.fixture
def student_token(client):
    return register_and_login(client, "student@test.com", "student123", "student", "Student User")


@pytest.fixture
def course(client, admin_token):
    return create_course_as_admin(client, admin_token)


class TestListCourses:
    def test_list_courses_public(self, client):
        resp = client.get("/api/v1/courses/")
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    def test_list_courses_returns_only_active(self, client, admin_token):
        create_course_as_admin(client, admin_token, code="A1")
        create_course_as_admin(client, admin_token, code="A2")
        # Deactivate one
        courses = client.get("/api/v1/courses/").json()
        client.put(
            f"/api/v1/courses/{courses[0]['id']}",
            json={"is_active": False},
            headers=auth_headers(admin_token),
        )
        resp = client.get("/api/v1/courses/")
        assert all(c["is_active"] for c in resp.json())


class TestGetCourse:
    def test_get_existing_course(self, client, course):
        resp = client.get(f"/api/v1/courses/{course['id']}")
        assert resp.status_code == 200
        assert resp.json()["code"] == course["code"]

    def test_get_nonexistent_course(self, client):
        resp = client.get("/api/v1/courses/9999")
        assert resp.status_code == 404


class TestCreateCourse:
    def test_admin_can_create_course(self, client, admin_token):
        resp = client.post(
            "/api/v1/courses/",
            json={"title": "Data Science", "code": "DS101", "capacity": 20},
            headers=auth_headers(admin_token),
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["code"] == "DS101"
        assert data["capacity"] == 20
        assert data["is_active"] is True

    def test_student_cannot_create_course(self, client, student_token):
        resp = client.post(
            "/api/v1/courses/",
            json={"title": "Data Science", "code": "DS101", "capacity": 20},
            headers=auth_headers(student_token),
        )
        assert resp.status_code == 403

    def test_unauthenticated_cannot_create_course(self, client):
        resp = client.post(
            "/api/v1/courses/",
            json={"title": "Data Science", "code": "DS101", "capacity": 20},
        )
        assert resp.status_code == 401

    def test_duplicate_course_code_rejected(self, client, admin_token):
        client.post(
            "/api/v1/courses/",
            json={"title": "Course 1", "code": "SAME", "capacity": 10},
            headers=auth_headers(admin_token),
        )
        resp = client.post(
            "/api/v1/courses/",
            json={"title": "Course 2", "code": "SAME", "capacity": 5},
            headers=auth_headers(admin_token),
        )
        assert resp.status_code == 400

    def test_zero_capacity_rejected(self, client, admin_token):
        resp = client.post(
            "/api/v1/courses/",
            json={"title": "Empty Course", "code": "EMP1", "capacity": 0},
            headers=auth_headers(admin_token),
        )
        assert resp.status_code == 422

    def test_negative_capacity_rejected(self, client, admin_token):
        resp = client.post(
            "/api/v1/courses/",
            json={"title": "Negative", "code": "NEG1", "capacity": -5},
            headers=auth_headers(admin_token),
        )
        assert resp.status_code == 422

    def test_empty_title_rejected(self, client, admin_token):
        resp = client.post(
            "/api/v1/courses/",
            json={"title": "  ", "code": "T101", "capacity": 10},
            headers=auth_headers(admin_token),
        )
        assert resp.status_code == 422


class TestUpdateCourse:
    def test_admin_can_update_course(self, client, admin_token, course):
        resp = client.put(
            f"/api/v1/courses/{course['id']}",
            json={"title": "Updated Title", "capacity": 50},
            headers=auth_headers(admin_token),
        )
        assert resp.status_code == 200
        assert resp.json()["title"] == "Updated Title"
        assert resp.json()["capacity"] == 50

    def test_admin_can_deactivate_course(self, client, admin_token, course):
        resp = client.put(
            f"/api/v1/courses/{course['id']}",
            json={"is_active": False},
            headers=auth_headers(admin_token),
        )
        assert resp.status_code == 200
        assert resp.json()["is_active"] is False

    def test_student_cannot_update_course(self, client, student_token, course):
        resp = client.put(
            f"/api/v1/courses/{course['id']}",
            json={"title": "Hacked"},
            headers=auth_headers(student_token),
        )
        assert resp.status_code == 403

    def test_update_to_duplicate_code_rejected(self, client, admin_token):
        create_course_as_admin(client, admin_token, code="FIRST")
        c2 = create_course_as_admin(client, admin_token, code="SECOND", title="Course 2")
        resp = client.put(
            f"/api/v1/courses/{c2['id']}",
            json={"code": "FIRST"},
            headers=auth_headers(admin_token),
        )
        assert resp.status_code == 400

    def test_update_nonexistent_course(self, client, admin_token):
        resp = client.put(
            "/api/v1/courses/9999",
            json={"title": "Ghost"},
            headers=auth_headers(admin_token),
        )
        assert resp.status_code == 404


class TestDeleteCourse:
    def test_admin_can_delete_course(self, client, admin_token, course):
        resp = client.delete(
            f"/api/v1/courses/{course['id']}",
            headers=auth_headers(admin_token),
        )
        assert resp.status_code == 204
        assert client.get(f"/api/v1/courses/{course['id']}").status_code == 404

    def test_student_cannot_delete_course(self, client, student_token, course):
        resp = client.delete(
            f"/api/v1/courses/{course['id']}",
            headers=auth_headers(student_token),
        )
        assert resp.status_code == 403

    def test_delete_nonexistent_course(self, client, admin_token):
        resp = client.delete("/api/v1/courses/9999", headers=auth_headers(admin_token))
        assert resp.status_code == 404