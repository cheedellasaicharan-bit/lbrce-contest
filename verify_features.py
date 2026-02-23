import requests

def test_routes():
    base_url = "http://127.0.0.1:5000"
    
    # Test 1: Leaderboard Restriction (should redirect to login or show error)
    print("Testing /leaderboard access...")
    try:
        r = requests.get(f"{base_url}/leaderboard", allow_redirects=False)
        print(f"Status Code: {r.status_code}")
        if r.status_code == 302:
            print("✅ Leaderboard successfully redirected (Restricted)")
        else:
            print("❌ Leaderboard is still public or returned unexpected status")
    except Exception as e:
        print(f"Error connecting: {e}")

    # Test 2: Forgot Password Page
    print("\nTesting /forgot-password page...")
    try:
        r = requests.get(f"{base_url}/forgot-password")
        if r.status_code == 200 and "Reset Password" in r.text:
            print("✅ Forgot Password page is accessible")
        else:
            print(f"❌ Forgot Password page failed (Status: {r.status_code})")
    except Exception as e:
        print(f"Error connecting: {e}")

if __name__ == "__main__":
    test_routes()
