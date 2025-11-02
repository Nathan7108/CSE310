import requests
import json
import sys
from datetime import datetime
from typing import Dict, Optional, Tuple
from flask import Flask, render_template, request, jsonify
import os

# Configure Flask to use frontend directories
app = Flask(__name__, 
            template_folder='../frontend',
            static_folder='../frontend/static')

class SpaceXAPIClient:
    # SpaceX API client for fetching launch data
    
    def __init__(self):
        self.base_url = "https://api.spacexdata.com/v5"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'SpaceXAPIClient/1.0'
        })
    
    def get_latest_launch(self) -> Tuple[bool, Dict]:
        # Get latest SpaceX launch
        try:
            url = f"{self.base_url}/launches/latest"
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            return True, data
        except Exception as e:
            return False, {"error": f"Failed to fetch latest launch: {str(e)}"}
    
    def get_launch_by_id(self, launch_id: str) -> Tuple[bool, Dict]:
        # Get specific launch by ID
        try:
            url = f"{self.base_url}/launches/{launch_id}"
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            return True, data
        except Exception as e:
            return False, {"error": f"Failed to fetch launch data: {str(e)}"}
    
    def test_connection(self) -> bool:
        # Test API connection
        try:
            success, data = self.get_latest_launch()
            return success
        except Exception:
            return False

# Initialize the SpaceX API client
spacex_client = SpaceXAPIClient()

# Flask Routes
@app.route('/')
def index():
    # Main page with SpaceX launch data
    return render_template('index.html')

@app.route('/api/latest')
def get_latest_launch():
    # Get latest SpaceX launch from Launch Library 2 API
    try:
        url = "https://ll.thespacedevs.com/2.2.0/launch/previous/?format=json&limit=50&search=SpaceX&net__lt=2024-12-31T23:59:59Z"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        if data.get('results') and len(data['results']) > 0:
            # Filter for past launches only
            current_time = datetime.now()
            past_launches = []
            
            for launch in data['results']:
                launch_date_str = launch.get('net', '')
                if launch_date_str:
                    try:
                        launch_date = datetime.fromisoformat(launch_date_str.replace('Z', '+00:00'))
                        if launch_date < current_time:
                            past_launches.append(launch)
                    except:
                        # If date parsing fails, include it (might be a different format)
                        past_launches.append(launch)
            
            if not past_launches:
                return jsonify({
                    'success': False,
                    'error': 'No past SpaceX launches found'
                }), 404
                
            launch = past_launches[0]
            
            # Convert to SpaceX API format for compatibility
            status_name = launch.get('status', {}).get('name', '').lower()
            is_successful = 'success' in status_name or 'successful' in status_name
            
            formatted_launch = {
                'id': str(launch.get('id', '')),
                'name': launch.get('name', 'Unknown Mission'),
                'date_utc': launch.get('net', ''),
                'success': is_successful,
                'flight_number': launch.get('launch_service_provider', {}).get('id', 0),
                'details': launch.get('mission', {}).get('description', ''),
                'links': {
                    'webcast': launch.get('vidURLs', [{}])[0].get('url', '') if launch.get('vidURLs') else '',
                    'article': launch.get('infoURLs', [{}])[0].get('url', '') if launch.get('infoURLs') else '',
                    'wikipedia': launch.get('infoURLs', [{}])[1].get('url', '') if len(launch.get('infoURLs', [])) > 1 else ''
                },
                'cores': []  # Launch Library doesn't have core data
            }
            
            return jsonify({
                'success': True,
                'data': formatted_launch
            })
        else:
            return jsonify({
                'success': False,
                'error': 'No recent SpaceX launches found'
            }), 404
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Server error: {str(e)}'
        }), 500

@app.route('/api/launch/<launch_id>')
def get_launch_by_id(launch_id):
    # Get specific launch by ID from Launch Library 2 API
    try:
        url = f"https://ll.thespacedevs.com/2.2.0/launch/{launch_id}/?format=json"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        launch = response.json()
        
        # Convert to SpaceX API format for compatibility
        status_name = launch.get('status', {}).get('name', '').lower()
        is_successful = 'success' in status_name or 'successful' in status_name
        
        formatted_launch = {
            'id': str(launch.get('id', '')),
            'name': launch.get('name', 'Unknown Mission'),
            'date_utc': launch.get('net', ''),
            'success': is_successful,
            'flight_number': launch.get('launch_service_provider', {}).get('id', 0),
            'details': launch.get('mission', {}).get('description', ''),
            'links': {
                'webcast': launch.get('vidURLs', [{}])[0].get('url', '') if launch.get('vidURLs') else '',
                'article': launch.get('infoURLs', [{}])[0].get('url', '') if launch.get('infoURLs') else '',
                'wikipedia': launch.get('infoURLs', [{}])[1].get('url', '') if len(launch.get('infoURLs', [])) > 1 else ''
            },
            'cores': []  # Launch Library doesn't have core data
        }
        
        return jsonify({
            'success': True,
            'data': formatted_launch
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Launch not found: {str(e)}'
        }), 404

@app.route('/api/launches')
def get_all_launches():
    # Get recent SpaceX launches from Launch Library 2 API
    try:
        url = "https://ll.thespacedevs.com/2.2.0/launch/previous/?format=json&limit=50&search=SpaceX&net__lt=2024-12-31T23:59:59Z"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        if data.get('results'):
            # Filter for past launches only
            current_time = datetime.now()
            past_launches = []
            
            for launch in data['results']:
                launch_date_str = launch.get('net', '')
                if launch_date_str:
                    try:
                        launch_date = datetime.fromisoformat(launch_date_str.replace('Z', '+00:00'))
                        if launch_date < current_time:
                            past_launches.append(launch)
                    except:
                        # If date parsing fails, include it (might be a different format)
                        past_launches.append(launch)
            
            if not past_launches:
                return jsonify({
                    'success': False,
                    'error': 'No past SpaceX launches found'
                }), 404
                
            launches = []
            for launch in past_launches:
                # Convert to SpaceX API format for compatibility
                status_name = launch.get('status', {}).get('name', '').lower()
                is_successful = 'success' in status_name or 'successful' in status_name
                
                formatted_launch = {
                    'id': str(launch.get('id', '')),
                    'name': launch.get('name', 'Unknown Mission'),
                    'date_utc': launch.get('net', ''),
                    'success': is_successful,
                    'flight_number': launch.get('launch_service_provider', {}).get('id', 0),
                    'details': launch.get('mission', {}).get('description', ''),
                    'links': {
                        'webcast': launch.get('vidURLs', [{}])[0].get('url', '') if launch.get('vidURLs') else '',
                        'article': launch.get('infoURLs', [{}])[0].get('url', '') if launch.get('infoURLs') else '',
                        'wikipedia': launch.get('infoURLs', [{}])[1].get('url', '') if len(launch.get('infoURLs', [])) > 1 else ''
                    },
                    'cores': []  # Launch Library doesn't have core data
                }
                launches.append(formatted_launch)
            
            return jsonify({
                'success': True,
                'data': launches
            })
        else:
            return jsonify({
                'success': False,
                'error': 'No SpaceX launches found'
            }), 404
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Server error: {str(e)}'
        }), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)