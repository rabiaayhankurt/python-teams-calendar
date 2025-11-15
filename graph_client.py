"""Microsoft Graph API client for calendar operations."""
import requests
import msal
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from config import Config


class GraphAPIClient:
    """Client for interacting with Microsoft Graph API."""
    
    def __init__(self):
        """Initialize the Graph API client."""
        self.config = Config
        self.access_token = None
        self._authenticate()
    
    def _authenticate(self):
        """Authenticate with Microsoft Graph API using client credentials flow."""
        app = msal.ConfidentialClientApplication(
            self.config.CLIENT_ID,
            authority=self.config.AUTHORITY,
            client_credential=self.config.CLIENT_SECRET,
        )
        
        result = app.acquire_token_silent(self.config.SCOPE, account=None)
        
        if not result:
            result = app.acquire_token_for_client(scopes=self.config.SCOPE)
        
        if "access_token" in result:
            self.access_token = result['access_token']
        else:
            raise Exception(f"Authentication failed: {result.get('error_description', 'Unknown error')}")
    
    def _get_headers(self) -> Dict[str, str]:
        """Get headers for API requests."""
        return {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }
    
    def get_schedule(
        self,
        emails: List[str],
        start_time: str,
        end_time: str,
        interval: int = 30
    ) -> Dict[str, Any]:
        """
        Get schedule information for specified users.
        
        Args:
            emails: List of participant email addresses
            start_time: Start time in ISO 8601 format (e.g., "2025-11-18T09:00:00")
            end_time: End time in ISO 8601 format
            interval: Interval in minutes (default: 30)
        
        Returns:
            Schedule data from Microsoft Graph API
        """
        url = f"{self.config.GRAPH_API_ENDPOINT}/users/me/calendar/getSchedule"
        
        payload = {
            "schedules": emails,
            "startTime": {
                "dateTime": start_time,
                "timeZone": "Europe/Istanbul"
            },
            "endTime": {
                "dateTime": end_time,
                "timeZone": "Europe/Istanbul"
            },
            "availabilityViewInterval": interval
        }
        
        response = requests.post(url, headers=self._get_headers(), json=payload)
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Failed to get schedule: {response.status_code} - {response.text}")
    
    def create_meeting(
        self,
        subject: str,
        start_time: str,
        end_time: str,
        attendees: List[str],
        body: Optional[str] = None,
        is_online: bool = True
    ) -> Dict[str, Any]:
        """
        Create a meeting event with Teams link.
        
        Args:
            subject: Meeting subject/title
            start_time: Start time in ISO 8601 format
            end_time: End time in ISO 8601 format
            attendees: List of attendee email addresses
            body: Optional meeting description
            is_online: Whether to create a Teams online meeting (default: True)
        
        Returns:
            Created event data from Microsoft Graph API
        """
        url = f"{self.config.GRAPH_API_ENDPOINT}/users/me/calendar/events"
        
        attendee_list = [
            {
                "emailAddress": {
                    "address": email,
                    "name": email.split('@')[0]
                },
                "type": "required"
            }
            for email in attendees
        ]
        
        payload = {
            "subject": subject,
            "body": {
                "contentType": "HTML",
                "content": body or "Toplantı detayları"
            },
            "start": {
                "dateTime": start_time,
                "timeZone": "Europe/Istanbul"
            },
            "end": {
                "dateTime": end_time,
                "timeZone": "Europe/Istanbul"
            },
            "attendees": attendee_list,
            "isOnlineMeeting": is_online,
            "onlineMeetingProvider": "teamsForBusiness" if is_online else None
        }
        
        response = requests.post(url, headers=self._get_headers(), json=payload)
        
        if response.status_code == 201:
            return response.json()
        else:
            raise Exception(f"Failed to create meeting: {response.status_code} - {response.text}")
    
    def find_meeting_times(
        self,
        attendees: List[str],
        start_date: str,
        end_date: str,
        time_range: str = "09:00-17:00",
        duration: int = 60
    ) -> Dict[str, Any]:
        """
        Find optimal meeting times using Microsoft Graph findMeetingTimes API.
        
        Args:
            attendees: List of participant email addresses
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            time_range: Time range (HH:MM-HH:MM)
            duration: Meeting duration in minutes (default: 60)
        
        Returns:
            Meeting time suggestions from Microsoft Graph API
        """
        url = f"{self.config.GRAPH_API_ENDPOINT}/users/me/findMeetingTimes"
        
        attendee_list = [
            {
                "type": "required",
                "emailAddress": {
                    "address": email
                }
            }
            for email in attendees
        ]
        
        # Parse time range
        start_hour, end_hour = time_range.split('-')
        
        payload = {
            "attendees": attendee_list,
            "timeConstraint": {
                "activityDomain": "work",
                "timeslots": [
                    {
                        "start": {
                            "dateTime": f"{start_date}T{start_hour}:00",
                            "timeZone": "Europe/Istanbul"
                        },
                        "end": {
                            "dateTime": f"{end_date}T{end_hour}:00",
                            "timeZone": "Europe/Istanbul"
                        }
                    }
                ]
            },
            "meetingDuration": f"PT{duration}M",
            "returnSuggestionReasons": True,
            "minimumAttendeePercentage": 50
        }
        
        response = requests.post(url, headers=self._get_headers(), json=payload)
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Failed to find meeting times: {response.status_code} - {response.text}")
