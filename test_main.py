"""
Comprehensive pytest tests for Task Management API.
"""

import pytest
import uuid
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from main import app, get_db, Base, TaskStatus


# Test Database Setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Override database dependency for testing."""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="function")
def test_db():
    """Create and clean up test database for each test."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(test_db):
    """Create test client."""
    return TestClient(app)


@pytest.fixture
def sample_task_data():
    """Sample task data for testing."""
    return {
        "name": "Test Task",
        "description": "This is a test task"
    }


@pytest.fixture
def sample_task_update():
    """Sample task update data for testing."""
    return {
        "name": "Updated Test Task",
        "description": "This is an updated test task",
        "status": "in_progress"
    }


class TestTaskCRUD:
    """Test CRUD operations for tasks."""
    
    def test_create_task_success(self, client, sample_task_data):
        """Test successful task creation."""
        response = client.post("/tasks/", json=sample_task_data)
        
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == sample_task_data["name"]
        assert data["description"] == sample_task_data["description"]
        assert data["status"] == "created"
        assert "uuid" in data
        assert "created_at" in data
        assert "updated_at" in data
    
    def test_create_task_without_description(self, client):
        """Test task creation without description."""
        task_data = {"name": "Task without description"}
        response = client.post("/tasks/", json=task_data)
        
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == task_data["name"]
        assert data["description"] is None
        assert data["status"] == "created"
    
    def test_create_task_validation_error(self, client):
        """Test task creation with validation errors."""
        # Empty name
        response = client.post("/tasks/", json={"name": ""})
        assert response.status_code == 422
        
        # Missing name
        response = client.post("/tasks/", json={"description": "Test"})
        assert response.status_code == 422
        
        # Name too long
        long_name = "a" * 256
        response = client.post("/tasks/", json={"name": long_name})
        assert response.status_code == 422
    
    def test_get_task_success(self, client, sample_task_data):
        """Test successful task retrieval."""
        # Create a task first
        create_response = client.post("/tasks/", json=sample_task_data)
        task_uuid = create_response.json()["uuid"]
        
        # Get the task
        response = client.get(f"/tasks/{task_uuid}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["uuid"] == task_uuid
        assert data["name"] == sample_task_data["name"]
        assert data["description"] == sample_task_data["description"]
    
    def test_get_task_not_found(self, client):
        """Test getting non-existent task."""
        fake_uuid = str(uuid.uuid4())
        response = client.get(f"/tasks/{fake_uuid}")
        
        assert response.status_code == 404
        assert response.json()["detail"] == "Task not found"
    
    def test_get_task_invalid_uuid(self, client):
        """Test getting task with invalid UUID."""
        response = client.get("/tasks/invalid-uuid")
        assert response.status_code == 422
    
    def test_get_tasks_list_empty(self, client):
        """Test getting empty tasks list."""
        response = client.get("/tasks/")
        
        assert response.status_code == 200
        assert response.json() == []
    
    def test_get_tasks_list_with_tasks(self, client, sample_task_data):
        """Test getting tasks list with existing tasks."""
        # Create multiple tasks
        task1_data = {**sample_task_data, "name": "Task 1"}
        task2_data = {**sample_task_data, "name": "Task 2"}
        
        client.post("/tasks/", json=task1_data)
        client.post("/tasks/", json=task2_data)
        
        response = client.get("/tasks/")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert any(task["name"] == "Task 1" for task in data)
        assert any(task["name"] == "Task 2" for task in data)
    
    def test_get_tasks_pagination(self, client, sample_task_data):
        """Test tasks list pagination."""
        # Create 5 tasks
        for i in range(5):
            task_data = {**sample_task_data, "name": f"Task {i}"}
            client.post("/tasks/", json=task_data)
        
        # Test pagination
        response = client.get("/tasks/?skip=2&limit=2")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
    
    def test_get_tasks_filter_by_status(self, client, sample_task_data):
        """Test filtering tasks by status."""
        # Create task and update its status
        create_response = client.post("/tasks/", json=sample_task_data)
        task_uuid = create_response.json()["uuid"]
        
        client.put(f"/tasks/{task_uuid}", json={"status": "in_progress"})
        
        # Create another task (status: created)
        client.post("/tasks/", json={**sample_task_data, "name": "Another Task"})
        
        # Filter by status
        response = client.get("/tasks/?status=in_progress")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["status"] == "in_progress"
    
    def test_update_task_success(self, client, sample_task_data, sample_task_update):
        """Test successful task update."""
        # Create a task first
        create_response = client.post("/tasks/", json=sample_task_data)
        task_uuid = create_response.json()["uuid"]
        
        # Update the task
        response = client.put(f"/tasks/{task_uuid}", json=sample_task_update)
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == sample_task_update["name"]
        assert data["description"] == sample_task_update["description"]
        assert data["status"] == sample_task_update["status"]
        assert data["updated_at"] != create_response.json()["updated_at"]
    
    def test_update_task_partial(self, client, sample_task_data):
        """Test partial task update."""
        # Create a task first
        create_response = client.post("/tasks/", json=sample_task_data)
        task_uuid = create_response.json()["uuid"]
        
        # Update only the name
        update_data = {"name": "Partially Updated Task"}
        response = client.put(f"/tasks/{task_uuid}", json=update_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == update_data["name"]
        assert data["description"] == sample_task_data["description"]  # Unchanged
        assert data["status"] == "created"  # Unchanged
    
    def test_update_task_not_found(self, client, sample_task_update):
        """Test updating non-existent task."""
        fake_uuid = str(uuid.uuid4())
        response = client.put(f"/tasks/{fake_uuid}", json=sample_task_update)
        
        assert response.status_code == 404
        assert response.json()["detail"] == "Task not found"
    
    def test_update_task_validation_error(self, client, sample_task_data):
        """Test task update with validation errors."""
        # Create a task first
        create_response = client.post("/tasks/", json=sample_task_data)
        task_uuid = create_response.json()["uuid"]
        
        # Try to update with invalid data
        response = client.put(f"/tasks/{task_uuid}", json={"name": ""})
        assert response.status_code == 422
        
        # Try to update with invalid status
        response = client.put(f"/tasks/{task_uuid}", json={"status": "invalid_status"})
        assert response.status_code == 422
    
    def test_delete_task_success(self, client, sample_task_data):
        """Test successful task deletion."""
        # Create a task first
        create_response = client.post("/tasks/", json=sample_task_data)
        task_uuid = create_response.json()["uuid"]
        
        # Delete the task
        response = client.delete(f"/tasks/{task_uuid}")
        
        assert response.status_code == 204
        
        # Verify task is deleted
        get_response = client.get(f"/tasks/{task_uuid}")
        assert get_response.status_code == 404
    
    def test_delete_task_not_found(self, client):
        """Test deleting non-existent task."""
        fake_uuid = str(uuid.uuid4())
        response = client.delete(f"/tasks/{fake_uuid}")
        
        assert response.status_code == 404
        assert response.json()["detail"] == "Task not found"


class TestTaskStatuses:
    """Test task status-related functionality."""
    
    def test_task_status_enum_values(self, client, sample_task_data):
        """Test all valid task status values."""
        # Create a task
        create_response = client.post("/tasks/", json=sample_task_data)
        task_uuid = create_response.json()["uuid"]
        
        # Test each status
        for status in ["created", "in_progress", "completed"]:
            response = client.put(f"/tasks/{task_uuid}", json={"status": status})
            assert response.status_code == 200
            assert response.json()["status"] == status
    
    def test_task_default_status(self, client, sample_task_data):
        """Test that new tasks have default 'created' status."""
        response = client.post("/tasks/", json=sample_task_data)
        
        assert response.status_code == 201
        assert response.json()["status"] == "created"


class TestHealthCheck:
    """Test health check endpoint."""
    
    def test_health_check(self, client):
        """Test health check endpoint."""
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data


class TestAPIDocumentation:
    """Test API documentation endpoints."""
    
    def test_swagger_docs(self, client):
        """Test Swagger documentation endpoint."""
        response = client.get("/docs")
        assert response.status_code == 200
    
    def test_redoc_docs(self, client):
        """Test ReDoc documentation endpoint."""
        response = client.get("/redoc")
        assert response.status_code == 200
    
    def test_openapi_schema(self, client):
        """Test OpenAPI schema endpoint."""
        response = client.get("/openapi.json")
        assert response.status_code == 200
        
        schema = response.json()
        assert "info" in schema
        assert "paths" in schema
        assert schema["info"]["title"] == "Task Management API"


class TestEdgeCases:
    """Test edge cases and error scenarios."""
    
    def test_concurrent_task_operations(self, client, sample_task_data):
        """Test concurrent operations on the same task."""
        # Create a task
        create_response = client.post("/tasks/", json=sample_task_data)
        task_uuid = create_response.json()["uuid"]
        
        # Simulate concurrent updates (in real scenario, these would be async)
        update1 = {"name": "Update 1"}
        update2 = {"name": "Update 2"}
        
        response1 = client.put(f"/tasks/{task_uuid}", json=update1)
        response2 = client.put(f"/tasks/{task_uuid}", json=update2)
        
        # Both should succeed (last one wins)
        assert response1.status_code == 200
        assert response2.status_code == 200
        
        # Verify final state
        get_response = client.get(f"/tasks/{task_uuid}")
        assert get_response.json()["name"] == "Update 2"
    
    def test_large_task_list(self, client, sample_task_data):
        """Test performance with larger task list."""
        # Create 50 tasks
        for i in range(50):
            task_data = {**sample_task_data, "name": f"Task {i:02d}"}
            response = client.post("/tasks/", json=task_data)
            assert response.status_code == 201
        
        # Get all tasks
        response = client.get("/tasks/")
        assert response.status_code == 200
        assert len(response.json()) == 50
    
    def test_unicode_task_names(self, client):
        """Test tasks with unicode characters."""
        unicode_task = {
            "name": "测试任务 🚀",
            "description": "Тестовое задание avec des caractères spéciaux"
        }
        
        response = client.post("/tasks/", json=unicode_task)
        assert response.status_code == 201
        
        data = response.json()
        assert data["name"] == unicode_task["name"]
        assert data["description"] == unicode_task["description"]


if __name__ == "__main__":
    pytest.main(["-v", "--tb=short"])