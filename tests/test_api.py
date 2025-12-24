"""
Test suite for the High School Management System API
"""

import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app import app, activities


@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset activities data before each test"""
    # Store original activities
    original_activities = {
        "Basketball": {
            "description": "Team sport focusing on basketball skills and competitions",
            "schedule": "Mondays and Wednesdays, 4:00 PM - 5:30 PM",
            "max_participants": 15,
            "participants": ["alex@mergington.edu"]
        },
        "Tennis Club": {
            "description": "Learn tennis techniques and participate in friendly matches",
            "schedule": "Saturdays, 10:00 AM - 12:00 PM",
            "max_participants": 10,
            "participants": ["sarah@mergington.edu"]
        },
        "Drama Club": {
            "description": "Perform in theatrical productions and develop acting skills",
            "schedule": "Thursdays, 4:00 PM - 5:30 PM",
            "max_participants": 25,
            "participants": ["lucas@mergington.edu", "isabella@mergington.edu"]
        },
        "Art Studio": {
            "description": "Explore painting, drawing, and sculpture techniques",
            "schedule": "Tuesdays and Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 18,
            "participants": ["mia@mergington.edu"]
        },
        "Debate Team": {
            "description": "Develop public speaking and argumentation skills",
            "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
            "max_participants": 16,
            "participants": ["james@mergington.edu", "grace@mergington.edu"]
        },
        "Science Club": {
            "description": "Conduct experiments and explore scientific concepts",
            "schedule": "Mondays, 4:00 PM - 5:30 PM",
            "max_participants": 20,
            "participants": ["thomas@mergington.edu"]
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
    
    # Reset activities to original state
    activities.clear()
    activities.update(original_activities)
    
    yield
    
    # Cleanup after test
    activities.clear()
    activities.update(original_activities)


class TestRootEndpoint:
    """Tests for the root endpoint"""
    
    def test_root_redirects_to_static(self, client):
        """Test that root endpoint redirects to static/index.html"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"


class TestGetActivities:
    """Tests for GET /activities endpoint"""
    
    def test_get_activities_returns_all_activities(self, client):
        """Test that GET /activities returns all activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert len(data) == 9
        assert "Basketball" in data
        assert "Tennis Club" in data
    
    def test_activities_have_required_fields(self, client):
        """Test that each activity has all required fields"""
        response = client.get("/activities")
        data = response.json()
        
        for activity_name, activity_data in data.items():
            assert "description" in activity_data
            assert "schedule" in activity_data
            assert "max_participants" in activity_data
            assert "participants" in activity_data
            assert isinstance(activity_data["participants"], list)


class TestSignupForActivity:
    """Tests for POST /activities/{activity_name}/signup endpoint"""
    
    def test_signup_for_existing_activity(self, client):
        """Test successful signup for an existing activity"""
        response = client.post("/activities/Basketball/signup?email=newstudent@mergington.edu")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "newstudent@mergington.edu" in data["message"]
        assert "Basketball" in data["message"]
        
        # Verify participant was added
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert "newstudent@mergington.edu" in activities_data["Basketball"]["participants"]
    
    def test_signup_for_nonexistent_activity(self, client):
        """Test signup for an activity that doesn't exist"""
        response = client.post("/activities/NonexistentActivity/signup?email=test@mergington.edu")
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "not found" in data["detail"].lower()
    
    def test_signup_with_special_characters_in_activity_name(self, client):
        """Test signup with URL-encoded activity name"""
        response = client.post("/activities/Tennis%20Club/signup?email=newplayer@mergington.edu")
        assert response.status_code == 200
        
        # Verify participant was added
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert "newplayer@mergington.edu" in activities_data["Tennis Club"]["participants"]


class TestUnregisterFromActivity:
    """Tests for DELETE /activities/{activity_name}/unregister endpoint"""
    
    def test_unregister_existing_participant(self, client):
        """Test successfully unregistering an existing participant"""
        # First, verify the participant exists
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert "alex@mergington.edu" in activities_data["Basketball"]["participants"]
        
        # Unregister the participant
        response = client.delete("/activities/Basketball/unregister?email=alex@mergington.edu")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "alex@mergington.edu" in data["message"]
        
        # Verify participant was removed
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert "alex@mergington.edu" not in activities_data["Basketball"]["participants"]
    
    def test_unregister_nonexistent_participant(self, client):
        """Test unregistering a participant that isn't registered"""
        response = client.delete("/activities/Basketball/unregister?email=notregistered@mergington.edu")
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "not found" in data["detail"].lower()
    
    def test_unregister_from_nonexistent_activity(self, client):
        """Test unregistering from an activity that doesn't exist"""
        response = client.delete("/activities/NonexistentActivity/unregister?email=test@mergington.edu")
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "not found" in data["detail"].lower()
    
    def test_unregister_with_special_characters(self, client):
        """Test unregister with URL-encoded activity name"""
        response = client.delete("/activities/Tennis%20Club/unregister?email=sarah@mergington.edu")
        assert response.status_code == 200
        
        # Verify participant was removed
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert "sarah@mergington.edu" not in activities_data["Tennis Club"]["participants"]


class TestIntegration:
    """Integration tests for the complete workflow"""
    
    def test_complete_signup_and_unregister_workflow(self, client):
        """Test the complete workflow: signup and then unregister"""
        email = "workflow@mergington.edu"
        activity = "Drama Club"
        
        # Get initial count
        initial_response = client.get("/activities")
        initial_data = initial_response.json()
        initial_count = len(initial_data[activity]["participants"])
        
        # Sign up
        signup_response = client.post(f"/activities/{activity}/signup?email={email}")
        assert signup_response.status_code == 200
        
        # Verify signup
        after_signup = client.get("/activities")
        after_signup_data = after_signup.json()
        assert len(after_signup_data[activity]["participants"]) == initial_count + 1
        assert email in after_signup_data[activity]["participants"]
        
        # Unregister
        unregister_response = client.delete(f"/activities/{activity}/unregister?email={email}")
        assert unregister_response.status_code == 200
        
        # Verify unregister
        after_unregister = client.get("/activities")
        after_unregister_data = after_unregister.json()
        assert len(after_unregister_data[activity]["participants"]) == initial_count
        assert email not in after_unregister_data[activity]["participants"]
    
    def test_multiple_signups_to_different_activities(self, client):
        """Test that a student can sign up for multiple different activities"""
        email = "multisport@mergington.edu"
        
        # Sign up for Basketball
        response1 = client.post(f"/activities/Basketball/signup?email={email}")
        assert response1.status_code == 200
        
        # Sign up for Chess Club
        response2 = client.post(f"/activities/Chess%20Club/signup?email={email}")
        assert response2.status_code == 200
        
        # Verify both signups
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert email in activities_data["Basketball"]["participants"]
        assert email in activities_data["Chess Club"]["participants"]
