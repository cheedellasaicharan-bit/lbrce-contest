from app import app
from flask import session

app.config['TESTING'] = True
with app.test_client() as client:
    with client.session_transaction() as sess:
        sess['user'] = "testuser"
        sess['email'] = "testuser@gmail.com"
        sess['role'] = "student"
    
    response = client.get('/user/dashboard')
    print("STATUS CODE:", response.status_code)
    if response.status_code == 200:
        print("Dashboard rendered successfully.")
    else:
        print("ERROR:", response.data.decode('utf-8'))
