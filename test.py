import pytest
from app import app, db, User
from werkzeug.security import generate_password_hash


@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    client = app.test_client()

    with app.app_context():
        db.create_all()
        admin_user = User(username="adminuser", password=generate_password_hash("adminpassword",
                                                                                method='pbkdf2:sha256'),
                          role="admin")
        regular_user = User(username="regularuser", password=generate_password_hash("userpassword",
                                                                                    method='pbkdf2:sha256'))
        db.session.add(admin_user)
        db.session.add(regular_user)
        db.session.commit()
        yield client

    with app.app_context():
        db.session.remove()
        db.drop_all()


def test_register_user(client):
    response = client.post('/api/v1/register', json={
        "username": "newuser",
        "password": "password123"
    })
    assert response.status_code == 201
    data = response.get_json()
    assert 'message' in data


def test_login_user(client):
    response = client.post('/api/v1/login', json={
        "username": "adminuser",
        "password": "adminpassword"
    })
    assert response.status_code == 200
    data = response.get_json()
    assert 'access_token' in data


def test_add_database(client):
    login_response = client.post('/api/v1/login', json={
        "username": "adminuser",
        "password": "adminpassword"
    })
    token = login_response.get_json()["access_token"]

    response = client.post('/api/v1/database', json={
        "host": "localhost",
        "port": 3306,
        "username": "root",
        "password": "rootpassword",
        "database_name": "test_db"
    }, headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 201
    data = response.get_json()
    assert 'id' in data
