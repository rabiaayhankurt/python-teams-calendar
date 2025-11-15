"""
Test script for Meeting Planner Assistant API
"""
import requests
import json
from datetime import datetime, timedelta

# API Base URL
BASE_URL = "http://localhost:5000"

def test_health_check():
    """Test health check endpoint"""
    print("\n=== Testing Health Check ===")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 200

def test_find_meeting_times():
    """Test find meeting times endpoint"""
    print("\n=== Testing Find Meeting Times ===")
    
    # Calculate dates
    today = datetime.now()
    start_date = (today + timedelta(days=1)).strftime('%Y-%m-%d')
    end_date = (today + timedelta(days=5)).strftime('%Y-%m-%d')
    
    payload = {
        "startDate": start_date,
        "endDate": end_date,
        "timeRange": "09:00-17:00",
        "participants": [
            "user1@company.com",
            "user2@company.com"
        ],
        "duration": 60
    }
    
    print(f"Request: {json.dumps(payload, indent=2)}")
    
    response = requests.post(
        f"{BASE_URL}/api/find-meeting-times",
        json=payload
    )
    
    print(f"\nStatus: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    
    return response.status_code == 200

def test_check_availability():
    """Test check availability endpoint"""
    print("\n=== Testing Check Availability ===")
    
    # Calculate time slot
    tomorrow = datetime.now() + timedelta(days=1)
    tomorrow_10am = tomorrow.replace(hour=10, minute=0, second=0, microsecond=0)
    tomorrow_11am = tomorrow_10am + timedelta(hours=1)
    
    payload = {
        "participants": [
            "user1@company.com",
            "user2@company.com"
        ],
        "startTime": tomorrow_10am.strftime('%Y-%m-%dT%H:%M:%S'),
        "endTime": tomorrow_11am.strftime('%Y-%m-%dT%H:%M:%S')
    }
    
    print(f"Request: {json.dumps(payload, indent=2)}")
    
    response = requests.post(
        f"{BASE_URL}/api/check-availability",
        json=payload
    )
    
    print(f"\nStatus: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    
    return response.status_code == 200

def test_create_meeting():
    """Test create meeting endpoint"""
    print("\n=== Testing Create Meeting ===")
    print("⚠️  This will create an actual meeting in the calendar!")
    
    confirm = input("Do you want to proceed? (yes/no): ")
    if confirm.lower() != 'yes':
        print("Skipped.")
        return True
    
    # Calculate time slot
    tomorrow = datetime.now() + timedelta(days=1)
    tomorrow_2pm = tomorrow.replace(hour=14, minute=0, second=0, microsecond=0)
    tomorrow_3pm = tomorrow_2pm + timedelta(hours=1)
    
    payload = {
        "subject": "Test Toplantısı - Meeting Planner Assistant",
        "startTime": tomorrow_2pm.strftime('%Y-%m-%dT%H:%M:%S'),
        "endTime": tomorrow_3pm.strftime('%Y-%m-%dT%H:%M:%S'),
        "attendees": [
            "user1@company.com"
        ],
        "body": "Bu bir test toplantısıdır. Meeting Planner Assistant tarafından oluşturulmuştur."
    }
    
    print(f"Request: {json.dumps(payload, indent=2)}")
    
    response = requests.post(
        f"{BASE_URL}/api/create-meeting",
        json=payload
    )
    
    print(f"\nStatus: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    
    return response.status_code == 200

def main():
    """Run all tests"""
    print("=" * 50)
    print("Meeting Planner Assistant - API Test Suite")
    print("=" * 50)
    
    tests = [
        ("Health Check", test_health_check),
        ("Find Meeting Times", test_find_meeting_times),
        ("Check Availability", test_check_availability),
        ("Create Meeting", test_create_meeting),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            success = test_func()
            results[test_name] = "✅ PASSED" if success else "❌ FAILED"
        except Exception as e:
            results[test_name] = f"❌ ERROR: {str(e)}"
            print(f"\nError in {test_name}: {str(e)}")
    
    # Print summary
    print("\n" + "=" * 50)
    print("Test Summary")
    print("=" * 50)
    for test_name, result in results.items():
        print(f"{test_name}: {result}")
    print("=" * 50)

if __name__ == "__main__":
    main()
