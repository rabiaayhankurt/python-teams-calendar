"""Flask API for Meeting Planner Assistant."""
from flask import Flask, request, jsonify
from datetime import datetime
from mock_graph_client import MockGraphAPIClient
from meeting_analyzer import MeetingAnalyzer
from config import Config
from cors_config import init_cors
import traceback


app = Flask(__name__)
# Enable CORS for Power Platform
app = init_cors(app)


def get_graph_client():
    """Get appropriate Graph API client based on mode."""
    if Config.USE_MOCK_API:
        return MockGraphAPIClient()
    else:
        # Import real client only when needed
        from graph_client import GraphAPIClient
        return GraphAPIClient()


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'service': 'Meeting Planner Assistant',
        'mode': 'MOCK' if Config.USE_MOCK_API else 'PRODUCTION',
        'timestamp': datetime.utcnow().isoformat()
    })


@app.route('/api/find-meeting-times', methods=['POST'])
def find_meeting_times():
    """
    Find optimal meeting times for participants.
    
    Request body:
    {
        "startDate": "2025-11-18",
        "endDate": "2025-11-22",
        "timeRange": "09:00-17:00",
        "participants": ["user1@example.com", "user2@example.com"],
        "duration": 60  // optional, default 60 minutes
    }
    
    Response:
    {
        "success": true,
        "suggestions": [
            {
                "start_time": "2025-11-19T10:00:00+03:00",
                "end_time": "2025-11-19T11:00:00+03:00",
                "available_count": 4,
                "total_participants": 5,
                "availability_percentage": 80.0,
                "formatted": "19 Kasım 2025, 10:00 - 11:00 (4/5 katılımcı uygun, %80)"
            }
        ]
    }
    """
    try:
        data = request.get_json()
        
        # Validate input
        required_fields = ['startDate', 'endDate', 'timeRange', 'participants']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'error': f'Missing required field: {field}'
                }), 400
        
        start_date = data['startDate']
        end_date = data['endDate']
        time_range = data['timeRange']
        participants = data['participants']
        duration = data.get('duration', 60)
        
        if not isinstance(participants, list) or len(participants) == 0:
            return jsonify({
                'success': False,
                'error': 'Participants must be a non-empty list'
            }), 400
        
        # Initialize clients (mock or real based on config)
        graph_client = get_graph_client()
        analyzer = MeetingAnalyzer()
        
        # Generate date range slots
        date_slots = analyzer.generate_date_range_slots(start_date, end_date, time_range)
        
        all_time_slots = []
        
        # Query schedule for each day
        for slot_start, slot_end in date_slots:
            try:
                schedule_data = graph_client.get_schedule(
                    emails=participants,
                    start_time=slot_start,
                    end_time=slot_end,
                    interval=30
                )
                
                # Analyze the schedule data
                start_dt = datetime.fromisoformat(slot_start)
                time_slots = analyzer.analyze_schedule_data(
                    schedule_data=schedule_data,
                    start_time=start_dt,
                    interval_minutes=30,
                    duration_minutes=duration
                )
                
                all_time_slots.extend(time_slots)
                
            except Exception as e:
                print(f"Error processing slot {slot_start}: {str(e)}")
                continue
        
        # Get top suggestions
        top_suggestions = analyzer.get_top_suggestions(all_time_slots, top_n=5, min_percentage=50.0)
        
        # Format suggestions
        formatted_suggestions = []
        for suggestion in top_suggestions:
            formatted_suggestions.append({
                **suggestion,
                'formatted': analyzer.format_suggestion(suggestion)
            })
        
        return jsonify({
            'success': True,
            'suggestions': formatted_suggestions,
            'total_slots_analyzed': len(all_time_slots)
        })
        
    except Exception as e:
        print(f"Error in find_meeting_times: {str(e)}")
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/create-meeting', methods=['POST'])
def create_meeting():
    """
    Create a Teams meeting.
    
    Request body:
    {
        "subject": "Proje Toplantısı",
        "startTime": "2025-11-19T10:00:00",
        "endTime": "2025-11-19T11:00:00",
        "attendees": ["user1@example.com", "user2@example.com"],
        "body": "Toplantı açıklaması"  // optional
    }
    
    Response:
    {
        "success": true,
        "meeting": {
            "id": "event_id",
            "webLink": "https://...",
            "onlineMeeting": {
                "joinUrl": "https://teams.microsoft.com/..."
            }
        }
    }
    """
    try:
        data = request.get_json()
        
        # Validate input
        required_fields = ['subject', 'startTime', 'endTime', 'attendees']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'error': f'Missing required field: {field}'
                }), 400
        
        subject = data['subject']
        start_time = data['startTime']
        end_time = data['endTime']
        attendees = data['attendees']
        body = data.get('body', '')
        
        if not isinstance(attendees, list) or len(attendees) == 0:
            return jsonify({
                'success': False,
                'error': 'Attendees must be a non-empty list'
            }), 400
        
        # Initialize Graph client (mock or real based on config)
        graph_client = get_graph_client()
        
        # Create the meeting
        meeting = graph_client.create_meeting(
            subject=subject,
            start_time=start_time,
            end_time=end_time,
            attendees=attendees,
            body=body,
            is_online=True
        )
        
        return jsonify({
            'success': True,
            'meeting': {
                'id': meeting.get('id'),
                'webLink': meeting.get('webLink'),
                'onlineMeeting': meeting.get('onlineMeeting'),
                'subject': meeting.get('subject'),
                'start': meeting.get('start'),
                'end': meeting.get('end')
            }
        })
        
    except Exception as e:
        print(f"Error in create_meeting: {str(e)}")
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/check-availability', methods=['POST'])
def check_availability():
    """
    Check availability for a specific time slot.
    
    Request body:
    {
        "participants": ["user1@example.com", "user2@example.com"],
        "startTime": "2025-11-19T10:00:00",
        "endTime": "2025-11-19T11:00:00"
    }
    
    Response:
    {
        "success": true,
        "availability": {
            "available_count": 4,
            "total_participants": 5,
            "available_participants": [...],
            "busy_participants": [...]
        }
    }
    """
    try:
        data = request.get_json()
        
        # Validate input
        required_fields = ['participants', 'startTime', 'endTime']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'error': f'Missing required field: {field}'
                }), 400
        
        participants = data['participants']
        start_time = data['startTime']
        end_time = data['endTime']
        
        if not isinstance(participants, list) or len(participants) == 0:
            return jsonify({
                'success': False,
                'error': 'Participants must be a non-empty list'
            }), 400
        
        # Initialize clients (mock or real based on config)
        graph_client = get_graph_client()
        analyzer = MeetingAnalyzer().get_schedule(
            emails=participants,
            start_time=start_time,
            end_time=end_time,
            interval=30
        )
        
        # Analyze availability
        start_dt = datetime.fromisoformat(start_time)
        time_slots = analyzer.analyze_schedule_data(
            schedule_data=schedule_data,
            start_time=start_dt,
            interval_minutes=30,
            duration_minutes=60
        )
        
        if time_slots:
            slot = time_slots[0]
            return jsonify({
                'success': True,
                'availability': {
                    'available_count': slot['available_count'],
                    'total_participants': slot['total_participants'],
                    'availability_percentage': slot['availability_percentage'],
                    'available_participants': slot['available_participants'],
                    'busy_participants': slot['busy_participants']
                }
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Could not analyze availability'
            }), 500
        
    except Exception as e:
        print(f"Error in check_availability: {str(e)}")
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


if __name__ == '__main__':
    try:
        Config.validate()
        print("Configuration validated successfully")
        print(f"Starting Meeting Planner Assistant API on port {Config.FLASK_PORT}")
        app.run(
            host='0.0.0.0',
            port=Config.FLASK_PORT,
            debug=Config.FLASK_DEBUG
        )
    except ValueError as e:
        print(f"Configuration error: {e}")
        print("Please copy .env.template to .env and fill in your credentials")
