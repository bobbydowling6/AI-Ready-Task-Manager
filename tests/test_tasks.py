def test_create_task(client, auth_headers):
    response = client.post(
        "/tasks/",
        json={
            "title": "Complete AI Project",
            "description": "Finish the task manager API",
            "priority": "High",
        },
        headers=auth_headers,
    )

    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Complete AI Project"
    assert data["description"] == "Finish the task manager API"
    assert data["priority"] == "High"
    assert data["is_completed"] is False
    assert "id" in data


def test_list_tasks(client, auth_headers):
    client.post(
        "/tasks/",
        json={"title": "Listed Task", "description": "Should appear in list"},
        headers=auth_headers,
    )

    response = client.get("/tasks/")

    assert response.status_code == 200
    tasks = response.json()
    assert len(tasks) >= 1
    assert any(task["title"] == "Listed Task" for task in tasks)


def test_get_task(client, auth_headers):
    create_response = client.post(
        "/tasks/",
        json={"title": "Single Task", "description": "Fetch by ID"},
        headers=auth_headers,
    )
    task_id = create_response.json()["id"]

    response = client.get(f"/tasks/{task_id}")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == task_id
    assert data["title"] == "Single Task"
    assert data["description"] == "Fetch by ID"


def test_create_task_requires_authentication(client):
    response = client.post(
        "/tasks/",
        json={"title": "Unauthorized Task", "description": "Should fail"},
    )

    assert response.status_code == 401


def test_get_nonexistent_task_returns_404(client):
    response = client.get("/tasks/9999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Task with id 9999 not found"
