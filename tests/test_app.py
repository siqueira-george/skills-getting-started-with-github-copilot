"""
Tests for the Mergington High School API
"""

import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add src directory to path so we can import app
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app import app, activities

@pytest.fixture
def client():
    """Provide a test client for the API"""
    return TestClient(app)

@pytest.fixture
def reset_activities():
    """Reset activities to their initial state before each test"""
    # Store original state
    original_activities = {
        "Basketball Club": {
            "description": "Join our competitive basketball team and participate in games",
            "schedule": "Mondays and Wednesdays, 4:00 PM - 5:30 PM",
            "max_participants": 15,
            "participants": ["alex@mergington.edu"]
        },
        "Tennis Team": {
            "description": "Develop tennis skills and compete in matches",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 5:00 PM",
            "max_participants": 10,
            "participants": ["ryan@mergington.edu"]
        },
        "Art Studio": {
            "description": "Explore painting, drawing, and sculpture techniques",
            "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
            "max_participants": 18,
            "participants": ["isabella@mergington.edu", "lucas@mergington.edu"]
        },
        "Drama Club": {
            "description": "Perform in theatrical productions and develop acting skills",
            "schedule": "Mondays and Thursdays, 4:00 PM - 5:30 PM",
            "max_participants": 25,
            "participants": ["mia@mergington.edu"]
        },
        "Debate Team": {
            "description": "Develop argumentation skills and compete in debate competitions",
            "schedule": "Tuesdays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["andrew@mergington.edu", "sophie@mergington.edu"]
        },
        "Robotics Club": {
            "description": "Build and program robots for competitions",
            "schedule": "Fridays, 3:30 PM - 5:30 PM",
            "max_participants": 16,
            "participants": ["james@mergington.edu", "john@mergington.edu"]
        },
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": ["john@mergington.edu", "olivia@mergington.edu"]
        }
    }
    
    # Clear and restore activities
    activities.clear()
    activities.update(original_activities)
    
    yield
    
    # Clean up after test
    activities.clear()
    activities.update(original_activities)


class TestGetActivities:
    """Tests for the GET /activities endpoint"""
    
    def test_get_activities_returns_200(self, client, reset_activities):
        """Test that /activities returns status 200"""
        response = client.get("/activities")
        assert response.status_code == 200
    
    def test_get_activities_returns_dict(self, client, reset_activities):
        """Test that /activities returns a dictionary"""
        response = client.get("/activities")
        assert isinstance(response.json(), dict)
    
    def test_get_activities_contains_expected_activities(self, client, reset_activities):
        """Test that /activities contains all expected activities"""
        response = client.get("/activities")
        data = response.json()
        
        expected_activities = [
            "Basketball Club",
            "Tennis Team",
            "Art Studio",
            "Drama Club",
            "Debate Team",
            "Robotics Club",
            "Chess Club",
            "Programming Class",
            "Gym Class"
        ]
        
        for activity in expected_activities:
            assert activity in data
    
    def test_activity_has_required_fields(self, client, reset_activities):
        """Test that each activity has required fields"""
        response = client.get("/activities")
        data = response.json()
        
        required_fields = ["description", "schedule", "max_participants", "participants"]
        
        for activity_name, activity_data in data.items():
            for field in required_fields:
                assert field in activity_data, f"Field '{field}' missing from {activity_name}"


class TestSignupForActivity:
    """Tests for the POST /activities/{activity_name}/signup endpoint"""
    
    def test_signup_returns_200(self, client, reset_activities):
        """Test successful signup returns 200"""
        response = client.post(
            "/activities/Basketball Club/signup?email=newstudent@mergington.edu"
        )
        assert response.status_code == 200
    
    def test_signup_returns_success_message(self, client, reset_activities):
        """Test signup returns correct success message"""
        response = client.post(
            "/activities/Basketball Club/signup?email=newstudent@mergington.edu"
        )
        data = response.json()
        assert "message" in data
        assert "newstudent@mergington.edu" in data["message"]
        assert "Basketball Club" in data["message"]
    
    def test_signup_adds_participant(self, client, reset_activities):
        """Test that signup actually adds the participant"""
        email = "newstudent@mergington.edu"
        client.post(f"/activities/Basketball Club/signup?email={email}")
        
        response = client.get("/activities")
        data = response.json()
        assert email in data["Basketball Club"]["participants"]
    
    def test_signup_nonexistent_activity_returns_404(self, client, reset_activities):
        """Test signup for non-existent activity returns 404"""
        response = client.post(
            "/activities/Nonexistent Club/signup?email=student@mergington.edu"
        )
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]
    
    def test_duplicate_signup_returns_400(self, client, reset_activities):
        """Test that signing up twice returns 400 error"""
        email = "alex@mergington.edu"
        # alex is already signed up for Basketball Club
        response = client.post(
            f"/activities/Basketball Club/signup?email={email}"
        )
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"]
    
    def test_signup_multiple_students(self, client, reset_activities):
        """Test that multiple students can sign up for the same activity"""
        emails = ["student1@mergington.edu", "student2@mergington.edu", "student3@mergington.edu"]
        
        for email in emails:
            response = client.post(f"/activities/Tennis Team/signup?email={email}")
            assert response.status_code == 200
        
        response = client.get("/activities")
        data = response.json()
        for email in emails:
            assert email in data["Tennis Team"]["participants"]


class TestUnregisterFromActivity:
    """Tests for the POST /activities/{activity_name}/unregister endpoint"""
    
    def test_unregister_returns_200(self, client, reset_activities):
        """Test successful unregister returns 200"""
        email = "alex@mergington.edu"  # Already signed up for Basketball Club
        response = client.post(
            f"/activities/Basketball Club/unregister?email={email}"
        )
        assert response.status_code == 200
    
    def test_unregister_returns_success_message(self, client, reset_activities):
        """Test unregister returns correct success message"""
        email = "alex@mergington.edu"
        response = client.post(
            f"/activities/Basketball Club/unregister?email={email}"
        )
        data = response.json()
        assert "message" in data
        assert email in data["message"]
        assert "Basketball Club" in data["message"]
    
    def test_unregister_removes_participant(self, client, reset_activities):
        """Test that unregister actually removes the participant"""
        email = "alex@mergington.edu"
        client.post(f"/activities/Basketball Club/unregister?email={email}")
        
        response = client.get("/activities")
        data = response.json()
        assert email not in data["Basketball Club"]["participants"]
    
    def test_unregister_nonexistent_activity_returns_404(self, client, reset_activities):
        """Test unregister from non-existent activity returns 404"""
        response = client.post(
            "/activities/Nonexistent Club/unregister?email=student@mergington.edu"
        )
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]
    
    def test_unregister_not_signed_up_returns_400(self, client, reset_activities):
        """Test that unregistering a student not signed up returns 400"""
        email = "notstudent@mergington.edu"  # Not signed up for anything
        response = client.post(
            f"/activities/Basketball Club/unregister?email={email}"
        )
        assert response.status_code == 400
        assert "not signed up" in response.json()["detail"]
    
    def test_unregister_then_signup_again(self, client, reset_activities):
        """Test that a student can unregister and then sign up again"""
        email = "alex@mergington.edu"
        
        # First unregister
        response = client.post(
            f"/activities/Basketball Club/unregister?email={email}"
        )
        assert response.status_code == 200
        
        # Then sign up again
        response = client.post(
            f"/activities/Basketball Club/signup?email={email}"
        )
        assert response.status_code == 200
        
        # Verify they're signed up
        response = client.get("/activities")
        data = response.json()
        assert email in data["Basketball Club"]["participants"]


class TestRootEndpoint:
    """Tests for the root endpoint"""
    
    def test_root_redirects(self, client):
        """Test that root endpoint redirects to /static/index.html"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307  # Temporary redirect
        assert "/static/index.html" in response.headers["location"]
