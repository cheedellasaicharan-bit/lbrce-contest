from app import app
from flask import session

app.config['TESTING'] = True

with app.test_client() as client:
    with client.session_transaction() as sess:
        sess['user'] = "testuser"
        sess['email'] = "testuser@gmail.com"
        sess['role'] = "student"
    
    response = client.get('/contest')
    if response.status_code == 200:
        print("SUCCESS: 200 OK")
    elif response.status_code == 302:
        print("REDIRECT:", response.location)
    else:
        print("ERROR:", response.status_code, response.data.decode('utf-8'))
