"""
Gauge step implementations for Task Management API tests.
"""

import subprocess
import time
import requests
import json
import uuid
from getgauge.python import step, before_suite, after_suite, data_store


# Global configuration
API_BASE_URL = "http://localhost:8000"
API_PROCESS = None


@before_suite
def setup_test_environment():
    """Set up test environment before running tests."""
    data_store.suite["tasks"] = {}
    data_store.suite["api_responses"] = {}


@after_suite  
def cleanup_test_environment():
    """Clean up test environment after tests."""
    global API_PROCESS
    if API_PROCESS:
        API_PROCESS.terminate()
        API_PROCESS.wait()


@step("Start the API server")
def start_api_server():
    """Start the FastAPI server for testing."""
    global API_PROCESS
    try:
        # Start the API server
        API_PROCESS = subprocess.Popen(
            ["python", "main.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # Wait for server to start
        time.sleep(3)
        
        # Verify server is running
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        assert response.status_code == 200, "API server failed to start"
        
    except Exception as e:
        raise AssertionError(f"Failed to start API server: {str(e)}")


@step("Stop the API server")
def stop_api_server():
    """Stop the FastAPI server."""
    global API_PROCESS
    if API_PROCESS:
        API_PROCESS.terminate()
        API_PROCESS.wait()
        API_PROCESS = None


@step("Create a task with name <task_name> and description <task_description>")
def create_task(task_name, task_description):
    """Create a new task with specified name and description."""
    task_data = {
        "name": task_name,
        "description": task_description
    }
    
    response = requests.post(f"{API_BASE_URL}/tasks/", json=task_data)
    
    # Store response for later use
    data_store.suite["api_responses"]["create_task"] = response
    
    if response.status_code == 201:
        task = response.json()
        data_store.suite["tasks"][task_name] = task
        data_store.suite["current_task"] = task


@step("The task should be created successfully with status <expected_status>")
def verify_task_creation_status(expected_status):
    """Verify that the task was created with the expected status."""
    response = data_store.suite["api_responses"]["create_task"]
    assert response.status_code == 201, f"Expected status 201, got {response.status_code}"
    
    task = response.json()
    assert task["status"] == expected_status, f"Expected status {expected_status}, got {task['status']}"


@step("The task should have a valid UUID")
def verify_task_uuid():
    """Verify that the created task has a valid UUID."""
    task = data_store.suite["current_task"]
    task_uuid = task["uuid"]
    
    # Validate UUID format
    try:
        uuid.UUID(task_uuid)
    except ValueError:
        raise AssertionError(f"Invalid UUID format: {task_uuid}")


@step("Create multiple tasks with names <task_names>")
def create_multiple_tasks(task_names):
    """Create multiple tasks with specified names."""
    names = [name.strip().strip('"') for name in task_names.split(',')]
    created_tasks = []
    
    for name in names:
        task_data = {
            "name": name,
            "description": f"Description for {name}"
        }
        
        response = requests.post(f"{API_BASE_URL}/tasks/", json=task_data)
        assert response.status_code == 201, f"Failed to create task {name}"
        
        task = response.json()
        data_store.suite["tasks"][name] = task
        created_tasks.append(task)
    
    data_store.suite["created_tasks"] = created_tasks


@step("Get the created task by UUID")
def get_task_by_uuid():
    """Get the created task using its UUID."""
    task = data_store.suite["current_task"]
    task_uuid = task["uuid"]
    
    response = requests.get(f"{API_BASE_URL}/tasks/{task_uuid}")
    data_store.suite["api_responses"]["get_task"] = response
    
    if response.status_code == 200:
        data_store.suite["retrieved_task"] = response.json()


@step("The retrieved task should match the created task details")
def verify_retrieved_task():
    """Verify that the retrieved task matches the created task."""
    response = data_store.suite["api_responses"]["get_task"]
    assert response.status_code == 200, f"Expected status 200, got {response.status_code}"
    
    created_task = data_store.suite["current_task"]
    retrieved_task = data_store.suite["retrieved_task"]
    
    assert created_task["uuid"] == retrieved_task["uuid"]
    assert created_task["name"] == retrieved_task["name"]
    assert created_task["description"] == retrieved_task["description"]
    assert created_task["status"] == retrieved_task["status"]


@step("Update the task name to <new_name> and status to <new_status>")
def update_task(new_name, new_status):
    """Update the task with new name and status."""
    task = data_store.suite["current_task"]
    task_uuid = task["uuid"]
    
    update_data = {
        "name": new_name,
        "status": new_status
    }
    
    response = requests.put(f"{API_BASE_URL}/tasks/{task_uuid}", json=update_data)
    data_store.suite["api_responses"]["update_task"] = response
    
    if response.status_code == 200:
        updated_task = response.json()
        data_store.suite["current_task"] = updated_task
        data_store.suite["updated_task"] = updated_task


@step("The task should be updated successfully")
def verify_task_update():
    """Verify that the task was updated successfully."""
    response = data_store.suite["api_responses"]["update_task"]
    assert response.status_code == 200, f"Expected status 200, got {response.status_code}"
    
    updated_task = response.json()
    assert "uuid" in updated_task
    assert "updated_at" in updated_task


@step("The updated_at timestamp should be different from created_at")
def verify_timestamp_difference():
    """Verify that updated_at is different from created_at."""
    updated_task = data_store.suite["updated_task"]
    
    created_at = updated_task["created_at"]
    updated_at = updated_task["updated_at"]
    
    assert created_at != updated_at, "updated_at should be different from created_at"


@step("Delete the created task")
def delete_task():
    """Delete the created task."""
    task = data_store.suite["current_task"]
    task_uuid = task["uuid"]
    
    response = requests.delete(f"{API_BASE_URL}/tasks/{task_uuid}")
    data_store.suite["api_responses"]["delete_task"] = response


@step("The task should be deleted successfully")
def verify_task_deletion():
    """Verify that the task was deleted successfully."""
    response = data_store.suite["api_responses"]["delete_task"]
    assert response.status_code == 204, f"Expected status 204, got {response.status_code}"


@step("Getting the deleted task should return 404 error")
def verify_deleted_task_not_found():
    """Verify that getting the deleted task returns 404."""
    task = data_store.suite["current_task"]
    task_uuid = task["uuid"]
    
    response = requests.get(f"{API_BASE_URL}/tasks/{task_uuid}")
    assert response.status_code == 404, f"Expected status 404, got {response.status_code}"


@step("Get the list of all tasks")
def get_all_tasks():
    """Get the list of all tasks."""
    response = requests.get(f"{API_BASE_URL}/tasks/")
    data_store.suite["api_responses"]["get_tasks"] = response
    
    if response.status_code == 200:
        data_store.suite["task_list"] = response.json()


@step("The list should contain <expected_count> tasks")
def verify_task_count(expected_count):
    """Verify that the task list contains the expected number of tasks."""
    response = data_store.suite["api_responses"]["get_tasks"]
    assert response.status_code == 200, f"Expected status 200, got {response.status_code}"
    
    task_list = data_store.suite["task_list"]
    actual_count = len(task_list)
    expected = int(expected_count)
    
    assert actual_count == expected, f"Expected {expected} tasks, got {actual_count}"


@step("Filter tasks by status <status>")
def filter_tasks_by_status(status):
    """Filter tasks by the specified status."""
    response = requests.get(f"{API_BASE_URL}/tasks/?status={status}")
    data_store.suite["api_responses"]["filter_tasks"] = response
    
    if response.status_code == 200:
        data_store.suite["filtered_tasks"] = response.json()


@step("All returned tasks should have status <expected_status>")
def verify_filtered_tasks_status(expected_status):
    """Verify that all filtered tasks have the expected status."""
    response = data_store.suite["api_responses"]["filter_tasks"]
    assert response.status_code == 200, f"Expected status 200, got {response.status_code}"
    
    filtered_tasks = data_store.suite["filtered_tasks"]
    
    for task in filtered_tasks:
        assert task["status"] == expected_status, f"Task {task['uuid']} has status {task['status']}, expected {expected_status}"


@step("Update task status from <old_status> to <new_status>")
def update_task_status(old_status, new_status):
    """Update task status from old to new status."""
    task = data_store.suite["current_task"]
    
    # Verify current status
    assert task["status"] == old_status, f"Expected current status {old_status}, got {task['status']}"
    
    # Update status
    task_uuid = task["uuid"]
    update_data = {"status": new_status}
    
    response = requests.put(f"{API_BASE_URL}/tasks/{task_uuid}", json=update_data)
    data_store.suite["api_responses"]["update_status"] = response
    
    if response.status_code == 200:
        updated_task = response.json()
        data_store.suite["current_task"] = updated_task


@step("Each status transition should be successful")
def verify_status_transition():
    """Verify that the status transition was successful."""
    response = data_store.suite["api_responses"]["update_status"]
    assert response.status_code == 200, f"Expected status 200, got {response.status_code}"


@step("Try to get a task with invalid UUID")
def try_get_invalid_uuid():
    """Try to get a task with an invalid UUID."""
    invalid_uuid = "invalid-uuid-format"
    response = requests.get(f"{API_BASE_URL}/tasks/{invalid_uuid}")
    data_store.suite["api_responses"]["invalid_uuid"] = response


@step("Should return 422 validation error")
def verify_validation_error():
    """Verify that a 422 validation error is returned."""
    response = data_store.suite["api_responses"]["invalid_uuid"]
    assert response.status_code == 422, f"Expected status 422, got {response.status_code}"


@step("Try to get a non-existent task with valid UUID")
def try_get_nonexistent_task():
    """Try to get a non-existent task with a valid UUID."""
    fake_uuid = str(uuid.uuid4())
    response = requests.get(f"{API_BASE_URL}/tasks/{fake_uuid}")
    data_store.suite["api_responses"]["nonexistent_task"] = response


@step("Should return 404 not found error")
def verify_not_found_error():
    """Verify that a 404 not found error is returned."""
    response = data_store.suite["api_responses"]["nonexistent_task"]
    assert response.status_code == 404, f"Expected status 404, got {response.status_code}"


@step("Try to create a task with empty name")
def try_create_invalid_task():
    """Try to create a task with an empty name."""
    invalid_task_data = {"name": "", "description": "Test"}
    response = requests.post(f"{API_BASE_URL}/tasks/", json=invalid_task_data)
    data_store.suite["api_responses"]["invalid_task"] = response


@step("Should return 422 validation error")
def verify_create_validation_error():
    """Verify that creating an invalid task returns 422."""
    response = data_store.suite["api_responses"]["invalid_task"]
    assert response.status_code == 422, f"Expected status 422, got {response.status_code}"


@step("Access Swagger documentation at /docs")
def access_swagger_docs():
    """Access the Swagger documentation endpoint."""
    response = requests.get(f"{API_BASE_URL}/docs")
    data_store.suite["api_responses"]["swagger_docs"] = response


@step("Should return 200 status code")
def verify_success_status():
    """Verify that the response has a 200 status code."""
    # Get the most recent response from context
    responses = data_store.suite["api_responses"]
    latest_key = list(responses.keys())[-1]
    response = responses[latest_key]
    
    assert response.status_code == 200, f"Expected status 200, got {response.status_code}"


@step("Access ReDoc documentation at /redoc")
def access_redoc_docs():
    """Access the ReDoc documentation endpoint."""
    response = requests.get(f"{API_BASE_URL}/redoc")
    data_store.suite["api_responses"]["redoc_docs"] = response


@step("Access OpenAPI schema at /openapi.json")
def access_openapi_schema():
    """Access the OpenAPI schema endpoint."""
    response = requests.get(f"{API_BASE_URL}/openapi.json")
    data_store.suite["api_responses"]["openapi_schema"] = response


@step("Should return valid JSON schema")
def verify_json_schema():
    """Verify that the response contains a valid JSON schema."""
    response = data_store.suite["api_responses"]["openapi_schema"]
    assert response.status_code == 200, f"Expected status 200, got {response.status_code}"
    
    try:
        schema = response.json()
        assert "info" in schema, "Schema should contain 'info' section"
        assert "paths" in schema, "Schema should contain 'paths' section"
    except json.JSONDecodeError:
        raise AssertionError("Response is not valid JSON")