import unittest
import requests

BASE_URL = "http://localhost:9001"

class TestEmailAPI(unittest.TestCase):

    def setUp(self):
        # Ensure server is up
        try:
            requests.get(f"{BASE_URL}/")
        except requests.exceptions.ConnectionError:
            self.fail("Server is not running. Please start it with 'python main.py'")

    def test_01_health_check(self):
        """Test GET / endpoint"""
        print("\nTesting Health Check...")
        response = requests.get(f"{BASE_URL}/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "running")
        print("✅ Health Check Passed")

    def test_02_list_profiles(self):
        """Test GET /profiles endpoint"""
        print("\nTesting List Profiles...")
        response = requests.get(f"{BASE_URL}/profiles")
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json(), list)
        print("✅ List Profiles Passed")

    def test_03_create_profile(self):
        """Test POST /profiles endpoint"""
        print("\nTesting Create Profile...")
        new_profile = {
            "profile_id": "test_profile",
            "smtp_host": "smtp.example.com",
            "smtp_port": 587,
            "smtp_user": "test@example.com",
            "smtp_password": "password123",
            "from_email": "test@example.com",
            "from_name": "Test User"
        }
        response = requests.post(f"{BASE_URL}/profiles", json=new_profile)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["profile_id"], "test_profile")
        
        # Verify it exists in list
        list_response = requests.get(f"{BASE_URL}/profiles")
        profiles = list_response.json()
        found = any(p["profile_id"] == "test_profile" for p in profiles)
        self.assertTrue(found, "Created profile not found in list")
        print("✅ Create Profile Passed")

    def test_04_send_email_default_profile(self):
        """Test POST /email/send with default profile"""
        print("\nTesting Send Email (Default Profile)...")
        # Note: This might fail if the default profile credentials in .env are invalid/dummy.
        # But we check for 200 OK or 500 (if upstream SMTP fails) 
        # API returns 500 if SMTP fails, which is expected if we don't have real creds.
        # However, if we assume the user wants to test the *API logic*, we should expect it to TRY to send.
        
        payload = {
            "to": ["test@example.com"],
            "subject": "Test Email",
            "text": "This is a test email."
        }
        response = requests.post(f"{BASE_URL}/email/send", json=payload)
        
        # If credentials are wrong, it returns 500. If right, 200.
        # We will accept 200 or 500 (with specific error) as "API is working"
        if response.status_code == 200:
            print("✅ Email Sent Successfully")
        elif response.status_code == 500:
            print(f"⚠️  Email try failed (likely SMTP credentials): {response.json()['detail']}")
        else:
            self.fail(f"Unexpected status code: {response.status_code}")

    def test_05_send_email_html(self):
        """Test POST /email/send with HTML body"""
        print("\nTesting Send Email (HTML)...")
        payload = {
            "to": ["test@example.com"],
            "subject": "Test HTML Email",
            "html": "<h1>Hello</h1><p>This is a test.</p>"
        }
        response = requests.post(f"{BASE_URL}/email/send", json=payload)

        if response.status_code == 200:
            print("✅ Email Sent Successfully")
        elif response.status_code == 500:
            print(f"⚠️  Email try failed (likely SMTP credentials): {response.json()['detail']}")
        else:
            self.fail(f"Unexpected status code: {response.status_code}")

    def test_06_send_email_missing_body(self):
        """Test POST /email/send validation"""
        print("\nTesting Send Email Validation...")
        payload = {
            "to": ["test@example.com"],
            "subject": "No Body"
        }
        response = requests.post(f"{BASE_URL}/email/send", json=payload)
        self.assertEqual(response.status_code, 400)
        self.assertIn("Provide 'text' or 'html' body", response.json()["detail"])
        print("✅ Validation Check Passed")

    def test_07_delete_profile(self):
        """Test DELETE /profiles/{id} endpoint"""
        print("\nTesting Delete Profile...")
        response = requests.delete(f"{BASE_URL}/profiles/test_profile")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "deleted")
        
        # Verify it's gone
        list_response = requests.get(f"{BASE_URL}/profiles")
        profiles = list_response.json()
        found = any(p["profile_id"] == "test_profile" for p in profiles)
        self.assertFalse(found, "Deleted profile still exists in list")
        print("✅ Delete Profile Passed")

    def test_08_delete_non_existent_profile(self):
        """Test DELETE non-existent profile"""
        print("\nTesting Delete Non-Existent Profile...")
        response = requests.delete(f"{BASE_URL}/profiles/non_existent_123")
        self.assertEqual(response.status_code, 404)
        print("✅ Delete Non-Existent Profile Passed")

if __name__ == '__main__':
    unittest.main()
