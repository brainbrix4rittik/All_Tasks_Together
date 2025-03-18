# tests/test_todo.py
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database import Base, get_db

# Create a test database
TEST_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    TEST_DATABASE_URL, 
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Override the get_db dependency for testing
def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

# Create the test client
client = TestClient(app)

# Setup and teardown for each test
def setup_module(module):
    Base.metadata.create_all(bind=engine)

def teardown_module(module):
    Base.metadata.drop_all(bind=engine)

def test_create_todo():
    # Test creating a todo
    response = client.post(
        "/todos/", 
        json={"title": "Test Todo", "description": "Test Description"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Test Todo"
    assert data["description"] == "Test Description"
    assert data["completed"] == False

def test_read_todos():
    # Create a todo first
    client.post("/todos/", json={"title": "Another Todo", "description": "Another Description"})
    
    # Read todos
    response = client.get("/todos/")
    assert response.status_code == 200
    todos = response.json()
    assert len(todos) > 0

def test_update_todo():
    # Create a todo
    create_response = client.post("/todos/", json={"title": "Update Todo"})
    todo_id = create_response.json()["id"]
    
    # Update the todo
    update_response = client.put(
        f"/todos/{todo_id}", 
        json={"completed": True, "title": "Updated Title"}
    )
    assert update_response.status_code == 200
    updated_todo = update_response.json()
    assert updated_todo["completed"] == True
    assert updated_todo["title"] == "Updated Title"

def test_delete_todo():
    # Create a todo
    create_response = client.post("/todos/", json={"title": "Delete Todo"})
    todo_id = create_response.json()["id"]
    
    # Delete the todo
    delete_response = client.delete(f"/todos/{todo_id}")
    assert delete_response.status_code == 200
