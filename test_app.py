import pytest
from app import app, get_db_connection

@pytest.fixture
def client():
    """Set up Flask test client and create in-memory SQLite DB."""
    app.config["TESTING"] = True
    with app.test_client() as client:
        with app.app_context():
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("DROP TABLE IF EXISTS feedback")
            cursor.execute("""
                CREATE TABLE feedback (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT,
                    message TEXT,
                    is_read BOOLEAN DEFAULT 0
                )
            """)
            conn.commit()
        yield client


def test_homepage(client):
    """Test that homepage loads correctly."""
    response = client.get('/')
    assert response.status_code == 200


def test_submit_feedback(client):
    """Test feedback submission with valid message."""
    response = client.post('/', data={
        'name': 'Alice',
        'message': 'Great class!'
    }, follow_redirects=True)

    assert response.status_code == 200


def test_submit_feedback_without_message(client):
    """Test feedback submission with empty message."""
    response = client.post('/', data={
        'name': 'Bob',
        'message': ''
    }, follow_redirects=True)

    assert response.status_code == 200
    # In case message text is not rendered in HTML, check redirect