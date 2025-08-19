#!/usr/bin/env python3
"""
Scheduled retraining script for effort estimation models.

This script is designed to be run periodically (e.g., monthly) to retrain
the effort estimation models with the new feedback data collected from users.
"""

import os
import sys
import logging
import argparse
from datetime import datetime
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Add project directory to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_root)

import model_retrainer
from feedback_collector import get_feedback_statistics

# Configure logging
LOG_DIR = "logs"
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

log_file = os.path.join(LOG_DIR, f"scheduled_retraining_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('scheduled_retrainer')

def send_notification_email(success, stats, results=None):
    """Send email notification about retraining results"""
    # This is a placeholder - implement with your email configuration
    
    # Email settings
    sender_email = os.environ.get("NOTIFICATION_EMAIL", "ai-system@example.com")
    receiver_emails = os.environ.get("ADMIN_EMAILS", "admin@example.com").split(',')
    smtp_server = os.environ.get("SMTP_SERVER", "smtp.example.com")
    smtp_port = int(os.environ.get("SMTP_PORT", "587"))
    smtp_user = os.environ.get("SMTP_USER", "")
    smtp_password = os.environ.get("SMTP_PASSWORD", "")
    
    # Skip if email settings not configured
    if not smtp_user or not smtp_password:
        logger.warning("Email notification skipped: SMTP credentials not configured")
        return
    
    try:
        # Create message
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = ', '.join(receiver_emails)
        
        if success:
            msg['Subject'] = f"AI Models Retraining Complete - {datetime.now().strftime('%Y-%m-%d')}"
            body = f"""
            <html>
              <body>
                <h2>Model Retraining Successful</h2>
                <p>The effort estimation models have been successfully retrained with the latest feedback data.</p>
                
                <h3>Feedback Statistics</h3>
                <ul>
                  <li>Total feedback entries: {stats.get('total_feedback', 0)}</li>
                  <li>Average estimation error: {stats.get('avg_estimation_error', 0):.2f}%</li>
                  <li>Last feedback received: {stats.get('last_feedback', 'N/A')}</li>
                </ul>
                
                <h3>Model Performance</h3>
                <table border="1" cellpadding="5">
                  <tr>
                    <th>Model</th>
                    <th>RMSE</th>
                    <th>MAE</th>
                    <th>R²</th>
                  </tr>
            """
            
            # Add model results
            if results:
                for model_name, metrics in results.items():
                    if isinstance(metrics, dict) and 'rmse' in metrics:
                        body += f"""
                        <tr>
                          <td>{model_name}</td>
                          <td>{metrics.get('rmse', 'N/A'):.4f}</td>
                          <td>{metrics.get('mae', 'N/A'):.4f}</td>
                          <td>{metrics.get('r2', 'N/A'):.4f}</td>
                        </tr>
                        """
            
            body += """
                </table>
                
                <p>The models have been automatically updated in production.</p>
                
                <p>This is an automated message from the AI Estimation System.</p>
              </body>
            </html>
            """
        else:
            msg['Subject'] = f"AI Models Retraining Failed - {datetime.now().strftime('%Y-%m-%d')}"
            body = f"""
            <html>
              <body>
                <h2>Model Retraining Failed</h2>
                <p>The effort estimation models retraining process encountered an error.</p>
                
                <h3>Feedback Statistics</h3>
                <ul>
                  <li>Total feedback entries: {stats.get('total_feedback', 0)}</li>
                  <li>Last feedback received: {stats.get('last_feedback', 'N/A')}</li>
                </ul>
                
                <p>Please check the logs for more information.</p>
                <p>Log file: {log_file}</p>
                
                <p>This is an automated message from the AI Estimation System.</p>
              </body>
            </html>
            """
        
        msg.attach(MIMEText(body, 'html'))
        
        # Connect to server and send email
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.send_message(msg)
        
        logger.info("Email notification sent successfully")
        
    except Exception as e:
        logger.error(f"Failed to send email notification: {e}")

def main():
    parser = argparse.ArgumentParser(description="Scheduled retraining for effort estimation models")
    parser.add_argument("--force", action="store_true", help="Force retraining even with minimal data")
    parser.add_argument("--notify", action="store_true", help="Send email notification about results")
    args = parser.parse_args()
    
    logger.info("Starting scheduled retraining process")
    
    # Get current feedback statistics
    feedback_stats = get_feedback_statistics()
    logger.info(f"Current feedback data: {feedback_stats['total_feedback']} entries")
    
    # Check if we have enough new data to retrain
    min_feedback_required = 5  # Adjust as needed
    
    if feedback_stats['total_feedback'] < min_feedback_required and not args.force:
        logger.info(f"Not enough feedback data for retraining. Minimum required: {min_feedback_required}")
        return
    
    # Proceed with retraining
    try:
        success = model_retrainer.retrain_models()
        
        # Get training results
        results = {}
        history_file = os.path.join(model_retrainer.RETRAINED_MODELS_DIR, "training_history.json")
        if os.path.exists(history_file):
            try:
                with open(history_file, 'r') as f:
                    history = json.load(f)
                    if history:
                        results = history[-1].get('results', {})
            except Exception as e:
                logger.error(f"Error reading training history: {e}")
        
        if success:
            logger.info("Model retraining completed successfully")
        else:
            logger.error("Model retraining failed")
        
        # Send notification if requested
        if args.notify:
            send_notification_email(success, feedback_stats, results)
            
    except Exception as e:
        logger.error(f"Error during scheduled retraining: {e}")
        if args.notify:
            send_notification_email(False, feedback_stats)

if __name__ == "__main__":
    main()
