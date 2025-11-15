"""Meeting availability analyzer to find optimal meeting times."""
from typing import List, Dict, Any, Tuple
from datetime import datetime, timedelta
import pytz


class MeetingAnalyzer:
    """Analyzes participant schedules to find optimal meeting times."""
    
    def __init__(self, timezone: str = "Europe/Istanbul"):
        """Initialize the analyzer with a timezone."""
        self.timezone = pytz.timezone(timezone)
    
    def parse_availability_view(self, availability_view: str) -> List[int]:
        """
        Parse availability view string from Graph API.
        
        Availability codes:
        0 = Free
        1 = Tentative
        2 = Busy
        3 = Out of Office
        4 = Working Elsewhere
        
        Args:
            availability_view: String of availability codes (e.g., "0022001")
        
        Returns:
            List of availability codes
        """
        return [int(code) for code in availability_view]
    
    def analyze_schedule_data(
        self,
        schedule_data: Dict[str, Any],
        start_time: datetime,
        interval_minutes: int = 30,
        duration_minutes: int = 60
    ) -> List[Dict[str, Any]]:
        """
        Analyze schedule data to find time slots with maximum availability.
        
        Args:
            schedule_data: Schedule data from Graph API getSchedule
            start_time: Start time of the search period
            interval_minutes: Interval in minutes for availability view
            duration_minutes: Desired meeting duration in minutes
        
        Returns:
            List of available time slots with participant information
        """
        schedules = schedule_data.get('value', [])
        
        if not schedules:
            return []
        
        # Get the length of availability view
        first_schedule = schedules[0]
        availability_length = len(first_schedule.get('availabilityView', ''))
        
        if availability_length == 0:
            return []
        
        # Calculate how many intervals needed for the meeting duration
        intervals_needed = duration_minutes // interval_minutes
        
        # Analyze each time slot
        time_slots = []
        
        for i in range(availability_length - intervals_needed + 1):
            slot_start = start_time + timedelta(minutes=i * interval_minutes)
            slot_end = slot_start + timedelta(minutes=duration_minutes)
            
            available_participants = []
            busy_participants = []
            
            for schedule in schedules:
                email = schedule.get('scheduleId', '')
                availability_view = schedule.get('availabilityView', '')
                
                if len(availability_view) <= i:
                    continue
                
                # Check if participant is available for the entire duration
                slot_availability = availability_view[i:i + intervals_needed]
                
                # Consider available if all intervals are 0 (Free) or 1 (Tentative)
                is_available = all(int(code) <= 1 for code in slot_availability)
                
                if is_available:
                    available_participants.append(email)
                else:
                    busy_participants.append(email)
            
            time_slots.append({
                'start_time': slot_start.isoformat(),
                'end_time': slot_end.isoformat(),
                'available_count': len(available_participants),
                'total_participants': len(schedules),
                'available_participants': available_participants,
                'busy_participants': busy_participants,
                'availability_percentage': (len(available_participants) / len(schedules) * 100) if schedules else 0
            })
        
        # Sort by available count (descending) and then by time
        time_slots.sort(key=lambda x: (-x['available_count'], x['start_time']))
        
        return time_slots
    
    def get_top_suggestions(
        self,
        time_slots: List[Dict[str, Any]],
        top_n: int = 5,
        min_percentage: float = 50.0
    ) -> List[Dict[str, Any]]:
        """
        Get top N meeting time suggestions.
        
        Args:
            time_slots: List of analyzed time slots
            top_n: Number of top suggestions to return
            min_percentage: Minimum availability percentage to consider
        
        Returns:
            Top N time slot suggestions
        """
        # Filter by minimum percentage
        filtered_slots = [
            slot for slot in time_slots
            if slot['availability_percentage'] >= min_percentage
        ]
        
        # Return top N
        return filtered_slots[:top_n]
    
    def format_suggestion(self, time_slot: Dict[str, Any]) -> str:
        """
        Format a time slot suggestion for display.
        
        Args:
            time_slot: Time slot data
        
        Returns:
            Formatted string
        """
        start = datetime.fromisoformat(time_slot['start_time'])
        end = datetime.fromisoformat(time_slot['end_time'])
        
        formatted_start = start.strftime('%d %B %Y, %H:%M')
        formatted_end = end.strftime('%H:%M')
        
        return (
            f"{formatted_start} - {formatted_end} "
            f"({time_slot['available_count']}/{time_slot['total_participants']} katılımcı uygun, "
            f"%{time_slot['availability_percentage']:.0f})"
        )
    
    def generate_date_range_slots(
        self,
        start_date: str,
        end_date: str,
        time_range: str = "09:00-17:00"
    ) -> List[Tuple[str, str]]:
        """
        Generate time slots for each day in the date range.
        
        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            time_range: Daily time range (HH:MM-HH:MM)
        
        Returns:
            List of (start_datetime, end_datetime) tuples in ISO format
        """
        start = datetime.strptime(start_date, '%Y-%m-%d')
        end = datetime.strptime(end_date, '%Y-%m-%d')
        
        start_hour, end_hour = time_range.split('-')
        
        time_slots = []
        current = start
        
        while current <= end:
            # Skip weekends (Saturday=5, Sunday=6)
            if current.weekday() < 5:
                slot_start = self.timezone.localize(
                    datetime.combine(current.date(), datetime.strptime(start_hour, '%H:%M').time())
                )
                slot_end = self.timezone.localize(
                    datetime.combine(current.date(), datetime.strptime(end_hour, '%H:%M').time())
                )
                
                time_slots.append((
                    slot_start.isoformat(),
                    slot_end.isoformat()
                ))
            
            current += timedelta(days=1)
        
        return time_slots
