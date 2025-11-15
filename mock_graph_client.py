"""Mock Microsoft Graph API client for testing without actual Graph API access."""
import random
from typing import List, Dict, Any
from datetime import datetime, timedelta
import pytz


class MockGraphAPIClient:
    """Mock client that simulates Microsoft Graph API responses."""
    
    def __init__(self):
        """Initialize the mock Graph API client."""
        self.timezone = pytz.timezone('Europe/Istanbul')
        print("⚠️  MOCK MODE: Using simulated data (no real Graph API calls)")
    
    def _authenticate(self):
        """Mock authentication - always succeeds."""
        pass
    
    def _generate_mock_availability(self, length: int) -> str:
        """
        Generate mock availability view string.
        
        0 = Free
        1 = Tentative  
        2 = Busy
        3 = Out of Office
        
        Args:
            length: Length of availability string
            
        Returns:
            String of availability codes
        """
        # Simulate realistic schedule: mostly free with some busy slots
        availability = []
        for _ in range(length):
            rand = random.random()
            if rand < 0.6:  # 60% free
                availability.append('0')
            elif rand < 0.75:  # 15% tentative
                availability.append('1')
            elif rand < 0.95:  # 20% busy
                availability.append('2')
            else:  # 5% out of office
                availability.append('3')
        return ''.join(availability)
    
    def get_schedule(
        self,
        emails: List[str],
        start_time: str,
        end_time: str,
        interval: int = 30
    ) -> Dict[str, Any]:
        """
        Mock get schedule - returns simulated availability.
        
        Args:
            emails: List of participant email addresses
            start_time: Start time in ISO 8601 format
            end_time: End time in ISO 8601 format
            interval: Interval in minutes (default: 30)
        
        Returns:
            Mock schedule data matching Graph API format
        """
        print(f"📅 MOCK: Getting schedule for {len(emails)} participants from {start_time} to {end_time}")
        
        # Calculate number of intervals
        start_dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
        end_dt = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
        duration_minutes = int((end_dt - start_dt).total_seconds() / 60)
        num_intervals = duration_minutes // interval
        
        # Generate mock schedules for each participant
        schedules = []
        for email in emails:
            schedules.append({
                "scheduleId": email,
                "availabilityView": self._generate_mock_availability(num_intervals),
                "scheduleItems": [],
                "workingHours": {
                    "daysOfWeek": ["monday", "tuesday", "wednesday", "thursday", "friday"],
                    "startTime": "09:00:00",
                    "endTime": "17:00:00",
                    "timeZone": {
                        "name": "Europe/Istanbul"
                    }
                }
            })
        
        return {
            "@odata.context": "https://graph.microsoft.com/v1.0/$metadata#Collection(microsoft.graph.scheduleInformation)",
            "value": schedules
        }
    
    def create_meeting(
        self,
        subject: str,
        start_time: str,
        end_time: str,
        attendees: List[str],
        body: str = None,
        is_online: bool = True
    ) -> Dict[str, Any]:
        """
        Mock create meeting - returns simulated meeting data.
        
        Args:
            subject: Meeting subject/title
            start_time: Start time in ISO 8601 format
            end_time: End time in ISO 8601 format
            attendees: List of attendee email addresses
            body: Optional meeting description
            is_online: Whether to create a Teams online meeting
        
        Returns:
            Mock event data matching Graph API format
        """
        print(f"✅ MOCK: Creating meeting '{subject}' with {len(attendees)} attendees")
        
        # Generate mock IDs
        event_id = f"MOCK_EVENT_{random.randint(100000, 999999)}"
        meeting_id = f"MOCK_MEETING_{random.randint(100000, 999999)}"
        
        mock_meeting = {
            "id": event_id,
            "subject": subject,
            "body": {
                "contentType": "HTML",
                "content": body or "Mock meeting - no real meeting created"
            },
            "start": {
                "dateTime": start_time,
                "timeZone": "Europe/Istanbul"
            },
            "end": {
                "dateTime": end_time,
                "timeZone": "Europe/Istanbul"
            },
            "location": {
                "displayName": "Microsoft Teams Meeting"
            },
            "attendees": [
                {
                    "emailAddress": {
                        "address": email,
                        "name": email.split('@')[0]
                    },
                    "type": "required"
                }
                for email in attendees
            ],
            "isOnlineMeeting": is_online,
            "onlineMeetingProvider": "teamsForBusiness" if is_online else None,
            "onlineMeeting": {
                "joinUrl": f"https://teams.microsoft.com/l/meetup-join/mock/{meeting_id}"
            } if is_online else None,
            "webLink": f"https://outlook.office365.com/calendar/item/mock/{event_id}",
            "createdDateTime": datetime.now(self.timezone).isoformat(),
            "lastModifiedDateTime": datetime.now(self.timezone).isoformat(),
            "isCancelled": False
        }
        
        return mock_meeting
    
    def find_meeting_times(
        self,
        attendees: List[str],
        start_date: str,
        end_date: str,
        time_range: str = "09:00-17:00",
        duration: int = 60
    ) -> Dict[str, Any]:
        """
        Mock find meeting times - returns simulated suggestions.
        
        Args:
            attendees: List of participant email addresses
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            time_range: Time range (HH:MM-HH:MM)
            duration: Meeting duration in minutes
        
        Returns:
            Mock meeting time suggestions
        """
        print(f"🔍 MOCK: Finding meeting times for {len(attendees)} attendees")
        
        # Generate some mock suggestions
        start_dt = datetime.strptime(start_date, '%Y-%m-%d')
        suggestions = []
        
        for i in range(5):
            suggestion_date = start_dt + timedelta(days=i)
            # Skip weekends
            if suggestion_date.weekday() >= 5:
                continue
                
            hour = 10 + (i * 2) % 7  # Vary the hours
            suggestion_time = self.timezone.localize(
                suggestion_date.replace(hour=hour, minute=0, second=0, microsecond=0)
            )
            
            suggestions.append({
                "meetingTimeSlot": {
                    "start": {
                        "dateTime": suggestion_time.isoformat(),
                        "timeZone": "Europe/Istanbul"
                    },
                    "end": {
                        "dateTime": (suggestion_time + timedelta(minutes=duration)).isoformat(),
                        "timeZone": "Europe/Istanbul"
                    }
                },
                "confidence": random.randint(60, 100),
                "organizerAvailability": "free",
                "attendeeAvailability": [
                    {
                        "emailAddress": email,
                        "availability": random.choice(["free", "free", "free", "tentative"])
                    }
                    for email in attendees
                ],
                "suggestionReason": "Attendees are available"
            })
        
        return {
            "@odata.context": "https://graph.microsoft.com/v1.0/$metadata#microsoft.graph.meetingTimeSuggestionsResult",
            "meetingTimeSuggestions": suggestions,
            "emptySuggestionsReason": ""
        }
