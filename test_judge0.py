<<<<<<< HEAD
import requests
import json

def test_judge0():
    url = "https://ce.judge0.com/submissions?wait=true"
    payload = {
        "source_code": "print('hello world')",
        "language_id": 71,
        "stdin": ""
    }
    headers = {
        "Content-Type": "application/json"
    }
    
    print(f"Connecting to {url}...")
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        if response.status_code == 201 or response.status_code == 200:
            data = response.json()
            stdout = data.get("stdout")
            print(f"STDOUT: {stdout}")
        else:
            print("Failed to get a successful response.")
    except Exception as e:
        print(f"Error occurred: {e}")

if __name__ == "__main__":
    test_judge0()
=======
import requests
import json

def test_judge0():
    url = "https://ce.judge0.com/submissions?wait=true"
    payload = {
        "source_code": "print('hello world')",
        "language_id": 71,
        "stdin": ""
    }
    headers = {
        "Content-Type": "application/json"
    }
    
    print(f"Connecting to {url}...")
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        if response.status_code == 201 or response.status_code == 200:
            data = response.json()
            stdout = data.get("stdout")
            print(f"STDOUT: {stdout}")
        else:
            print("Failed to get a successful response.")
    except Exception as e:
        print(f"Error occurred: {e}")

if __name__ == "__main__":
    test_judge0()
>>>>>>> master
