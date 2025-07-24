"""
Script to start the estimation service and integrate with task management
"""

import os
import sys
import argparse
import logging
import json
import requests
import time
from flask import Flask, request, jsonify
from threading import Thread
from api_server import app as api_app
from effort_estimation_service import EffortEstimationService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("service_integration.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("ServiceIntegration")

class TaskManagementIntegration:
    """
    Integration with task management service
    """
    
    def __init__(self, task_service_url):
        """
        Initialize integration with task management service
        
        Args:
            task_service_url (str): URL of the task management service
        """
        self.task_service_url = task_service_url
        self.estimation_service = EffortEstimationService()
        logger.info(f"Task Management Integration initialized with service URL: {task_service_url}")
    
    def register_estimation_service(self):
        """
        Register the estimation service with the task management service
        
        Returns:
            bool: True if registration successful, False otherwise
        """
        try:
            # Registration payload
            payload = {
                "service_name": "effort_estimation",
                "service_url": "http://localhost:5000/api",  # Local API server
                "capabilities": [
                    "estimate_effort",
                    "suggest_team",
                    "analyze_requirements",
                    "generate_report"
                ]
            }
            
            # Send registration request
            response = requests.post(
                f"{self.task_service_url}/api/services/register",
                json=payload
            )
            
            if response.status_code == 200:
                logger.info("Successfully registered estimation service")
                return True
            else:
                logger.error(f"Failed to register estimation service: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error registering estimation service: {e}")
            return False
    
    def listen_for_estimation_requests(self):
        """
        Listen for estimation requests from the task management service
        """
        logger.info("Starting to listen for estimation requests")
        
        # In a real implementation, this would use a message queue or webhook
        # For simplicity, we'll use polling
        
        while True:
            try:
                # Poll for estimation requests
                response = requests.get(
                    f"{self.task_service_url}/api/estimation/pending"
                )
                
                if response.status_code == 200:
                    requests_data = response.json()
                    
                    if 'requests' in requests_data and requests_data['requests']:
                        for req in requests_data['requests']:
                            # Process the estimation request
                            self._process_estimation_request(req)
                
                # Wait before polling again
                time.sleep(10)  # Poll every 10 seconds
                
            except Exception as e:
                logger.error(f"Error polling for estimation requests: {e}")
                time.sleep(30)  # Wait longer after an error
    
    def _process_estimation_request(self, request_data):
        """
        Process an estimation request from the task management service
        
        Args:
            request_data (dict): Estimation request data
        """
        try:
            request_id = request_data.get('id')
            request_type = request_data.get('type')
            requirements = request_data.get('requirements')
            project_name = request_data.get('project_name', 'Software Project')
            
            logger.info(f"Processing estimation request {request_id} of type {request_type}")
            
            # Different request types
            if request_type == 'estimate_effort':
                result = self.estimation_service.estimate_effort(requirements)
            elif request_type == 'suggest_team':
                result = self.estimation_service.suggest_team_composition(requirements)
            elif request_type == 'analyze_requirements':
                result = self.estimation_service.analyzer.analyze_requirements_document(requirements)
            elif request_type == 'generate_report':
                result = self.estimation_service.generate_estimation_report(requirements, project_name)
            else:
                logger.warning(f"Unknown request type: {request_type}")
                result = {"error": f"Unknown request type: {request_type}"}
            
            # Send the result back to the task management service
            self._send_estimation_result(request_id, result)
            
        except Exception as e:
            logger.error(f"Error processing estimation request {request_data.get('id')}: {e}")
            # Send error response
            self._send_estimation_result(
                request_data.get('id'),
                {"error": str(e)}
            )
    
    def _send_estimation_result(self, request_id, result):
        """
        Send estimation result back to the task management service
        
        Args:
            request_id (str): ID of the estimation request
            result (dict): Estimation result
        """
        try:
            # Prepare result payload
            payload = {
                "request_id": request_id,
                "result": result
            }
            
            # Send result
            response = requests.post(
                f"{self.task_service_url}/api/estimation/result",
                json=payload
            )
            
            if response.status_code == 200:
                logger.info(f"Successfully sent result for request {request_id}")
            else:
                logger.error(f"Failed to send result for request {request_id}: {response.text}")
                
        except Exception as e:
            logger.error(f"Error sending estimation result for request {request_id}: {e}")
    
    def start_integration(self):
        """
        Start the integration with task management service
        """
        # Register the estimation service
        if self.register_estimation_service():
            # Start listening for estimation requests in a separate thread
            thread = Thread(target=self.listen_for_estimation_requests)
            thread.daemon = True
            thread.start()
            
            logger.info("Task management integration started")
            return True
        else:
            logger.error("Failed to start task management integration")
            return False

def main():
    """
    Main function to start the estimation service and integration
    """
    parser = argparse.ArgumentParser(description='Start the estimation service and integrate with task management')
    parser.add_argument('--port', type=int, default=5000,
                        help='Port to run the API server on')
    parser.add_argument('--task-service-url', type=str, default='http://localhost:8000',
                        help='URL of the task management service')
    parser.add_argument('--skip-integration', action='store_true',
                        help='Skip integration with task management service')
    
    args = parser.parse_args()
    
    # Start the API server in a separate thread
    def run_api_server():
        api_app.run(host='0.0.0.0', port=args.port, debug=False, use_reloader=False)
    
    api_thread = Thread(target=run_api_server)
    api_thread.daemon = True
    api_thread.start()
    
    logger.info(f"API server started on port {args.port}")
    
    # Start integration with task management service if requested
    if not args.skip_integration:
        integration = TaskManagementIntegration(args.task_service_url)
        integration.start_integration()
    
    # Keep the main thread running
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Service stopping due to keyboard interrupt")
        sys.exit(0)

if __name__ == '__main__':
    main()
