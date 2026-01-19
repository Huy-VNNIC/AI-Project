"""
Populate OOD Template with Diverse Real Requirements

Collects requirements from:
1. Requirement datasets (ARFF files)
2. Manually curated examples from different domains
3. Public requirement datasets

Target: 200-500 diverse requirements for OOD evaluation
"""
import csv
import re
from pathlib import Path


# Manually curated diverse requirements (50+ examples)
CURATED_REQUIREMENTS = [
    # Banking & Finance
    ("banking", "The system must verify user identity through two-factor authentication using SMS or authenticator app."),
    ("banking", "Users should be able to transfer funds between their accounts instantly with real-time balance updates."),
    ("banking", "The application must encrypt all financial transactions using AES-256 encryption."),
    ("banking", "Customers need to view their transaction history for the past 12 months with filtering options."),
    ("banking", "The system shall send email notifications for transactions exceeding $1000."),
    ("banking", "Users must be able to report fraudulent transactions and freeze their accounts immediately."),
    ("banking", "The mobile app should support biometric authentication using fingerprint or face recognition."),
    ("banking", "The system must comply with PCI-DSS standards for payment card processing."),
    
    # E-commerce
    ("ecommerce", "Customers should be able to add products to their shopping cart and save them for later."),
    ("ecommerce", "The system must calculate shipping costs based on delivery address and package weight."),
    ("ecommerce", "Users need to track their order status in real-time from warehouse to delivery."),
    ("ecommerce", "The application should recommend related products based on browsing history and purchase patterns."),
    ("ecommerce", "Sellers must be able to manage their inventory levels and receive alerts for low stock."),
    ("ecommerce", "The checkout process should support multiple payment methods including credit cards, PayPal, and digital wallets."),
    ("ecommerce", "Customers should be able to write reviews and rate products they have purchased."),
    ("ecommerce", "The system must handle promotional codes and apply discounts automatically at checkout."),
    
    # Healthcare
    ("healthcare", "Doctors must be able to access patient medical records securely with role-based permissions."),
    ("healthcare", "The system should send appointment reminders to patients 24 hours before their scheduled time."),
    ("healthcare", "Patients need to view their lab results online once they are approved by their physician."),
    ("healthcare", "The application must maintain an audit log of all access to patient health information for HIPAA compliance."),
    ("healthcare", "Healthcare providers should be able to prescribe medications electronically to pharmacies."),
    ("healthcare", "The system must integrate with insurance providers to verify coverage before appointments."),
    ("healthcare", "Patients should be able to schedule, reschedule, or cancel appointments through the mobile app."),
    ("healthcare", "The telemedicine feature must support secure video consultations with end-to-end encryption."),
    
    # Education
    ("education", "Students should be able to enroll in courses online and view their class schedule."),
    ("education", "Teachers need to create and grade assignments with support for multiple question types."),
    ("education", "The system must track student attendance and generate reports for administrators."),
    ("education", "Students should receive notifications when new course materials are uploaded by instructors."),
    ("education", "The platform must support live virtual classrooms with screen sharing and breakout rooms."),
    ("education", "Parents should be able to monitor their child's academic progress and attendance records."),
    ("education", "The system must generate transcripts and certificates upon course completion."),
    ("education", "Students need to participate in discussion forums and collaborate on group projects online."),
    
    # IoT & Smart Home
    ("iot", "Users should be able to control smart lights remotely using their smartphone."),
    ("iot", "The system must monitor temperature and humidity levels and send alerts when thresholds are exceeded."),
    ("iot", "Smart locks should support multiple access methods including PIN codes, fingerprint, and smartphone."),
    ("iot", "The application should create automation rules based on time, location, or sensor triggers."),
    ("iot", "Users need to view real-time energy consumption data for all connected devices."),
    ("iot", "The system must detect unusual activity patterns and notify homeowners of potential security issues."),
    ("iot", "Smart cameras should record video when motion is detected and store it securely in the cloud."),
    ("iot", "Users should be able to integrate voice assistants for hands-free control of smart devices."),
    
    # HR & Recruitment
    ("hr", "HR managers must be able to post job openings and manage applicant tracking through the system."),
    ("hr", "Candidates should be able to apply for positions by uploading their resume and filling out an application form."),
    ("hr", "The system should automatically screen resumes based on required qualifications and keywords."),
    ("hr", "Hiring managers need to schedule interviews and send calendar invitations to candidates."),
    ("hr", "Employees should be able to submit time-off requests and view their leave balance online."),
    ("hr", "The application must track employee performance reviews and goal progress."),
    ("hr", "New hires should complete onboarding tasks and e-sign documents through the portal."),
    ("hr", "The system must generate payroll reports and integrate with accounting software."),
    
    # Logistics & Supply Chain
    ("logistics", "The system must track shipment locations in real-time using GPS data."),
    ("logistics", "Warehouse managers should be able to scan barcodes to update inventory levels automatically."),
    ("logistics", "The application must optimize delivery routes based on traffic conditions and delivery priorities."),
    ("logistics", "Customers need to receive SMS notifications when their package is out for delivery."),
    ("logistics", "The system should manage multiple warehouse locations and transfer inventory between them."),
    ("logistics", "Drivers must be able to capture proof of delivery with customer signatures and photos."),
    ("logistics", "The platform should forecast demand and suggest optimal reorder points for products."),
    ("logistics", "The system must integrate with shipping carriers to compare rates and generate labels."),
    
    # Social Media
    ("social", "Users should be able to create profiles with photos, bio, and personal information."),
    ("social", "The system must allow users to post text, images, and videos to their timeline."),
    ("social", "Users need to follow other users and see their posts in a personalized news feed."),
    ("social", "The application should implement content moderation to detect and remove inappropriate content."),
    ("social", "Users must be able to send direct messages and create group chats."),
    ("social", "The system should suggest friends based on mutual connections and shared interests."),
    ("social", "Users need to control privacy settings for who can view their posts and profile information."),
    ("social", "The platform must notify users of likes, comments, and mentions in real-time."),
    
    # CRM
    ("crm", "Sales representatives should be able to log customer interactions and track communication history."),
    ("crm", "The system must automatically assign leads to sales reps based on territory or workload."),
    ("crm", "Managers need to view sales pipeline and forecast revenue for the current quarter."),
    ("crm", "The application should send automated follow-up emails to prospects based on predefined schedules."),
    ("crm", "Users must be able to create custom fields and tags to categorize customers."),
    ("crm", "The system should integrate with email and calendar to sync appointments and correspondence."),
    ("crm", "Marketing teams need to create and track email campaigns with open and click-through rates."),
    ("crm", "The platform must generate reports on sales performance by rep, region, and product."),
    
    # Project Management
    ("project", "Team members should be able to create tasks and assign them to colleagues with due dates."),
    ("project", "The system must visualize project timelines using Gantt charts."),
    ("project", "Users need to track time spent on tasks and generate timesheets for billing."),
    ("project", "The application should send notifications when tasks are approaching their deadlines."),
    ("project", "Project managers must be able to view resource allocation across multiple projects."),
    ("project", "The system should support agile methodologies with sprint planning and burndown charts."),
    ("project", "Users need to attach files and documents to tasks for collaboration."),
    ("project", "The platform must integrate with version control systems to link commits to tasks."),
    
    # Cybersecurity
    ("security", "The system must detect and block suspicious login attempts after 3 failed attempts."),
    ("security", "Security analysts should receive alerts when potential threats are detected by the IDS."),
    ("security", "The application must enforce strong password policies with minimum complexity requirements."),
    ("security", "All API endpoints must require authentication and authorization before processing requests."),
    ("security", "The system should log all security events and store them for at least 90 days."),
    ("security", "Administrators need to perform regular vulnerability scans and review security reports."),
    ("security", "The platform must implement rate limiting to prevent denial-of-service attacks."),
    ("security", "User sessions must expire after 30 minutes of inactivity for security purposes."),
    
    # Gaming
    ("gaming", "Players should be able to create custom avatars with various cosmetic options."),
    ("gaming", "The system must support multiplayer matchmaking based on skill level and region."),
    ("gaming", "Users need to track their achievements, statistics, and leaderboard rankings."),
    ("gaming", "The game should save player progress automatically and support cloud saves."),
    ("gaming", "Players must be able to purchase in-game items using real money or virtual currency."),
    ("gaming", "The system should implement anti-cheat mechanisms to ensure fair gameplay."),
    ("gaming", "Users need to join or create guilds and communicate with guild members."),
    ("gaming", "The platform must support voice chat during gameplay with push-to-talk functionality."),
    
    # Real Estate
    ("realestate", "Users should be able to search for properties using filters like location, price, and property type."),
    ("realestate", "The system must display property listings with photos, descriptions, and virtual tours."),
    ("realestate", "Buyers need to schedule property viewings and receive confirmation notifications."),
    ("realestate", "Real estate agents should be able to manage their listings and update property information."),
    ("realestate", "The application must calculate mortgage estimates based on property price and down payment."),
    ("realestate", "Users should receive alerts when new properties matching their criteria become available."),
    ("realestate", "The system must integrate with MLS databases to sync property listings automatically."),
    ("realestate", "Buyers and sellers need to communicate through the platform with message history."),
]


def parse_arff_requirements(arff_path: Path) -> list:
    """Extract requirements from ARFF file"""
    requirements = []
    
    with open(arff_path, 'r', encoding='utf-8', errors='ignore') as f:
        in_data = False
        for line in f:
            line = line.strip()
            
            if line == '@data':
                in_data = True
                continue
            
            if not in_data or not line or line.startswith('%'):
                continue
            
            # Parse CSV line in ARFF
            parts = line.split('","')
            if len(parts) >= 3:
                req_text = parts[0].strip('"')
                label = parts[-1].strip('"')
                
                # Only relevant requirements
                if 'relevant' in label.lower():
                    # Convert underscore format to natural language
                    req_natural = req_text.replace('_', ' ')
                    if len(req_natural) > 20:  # Filter out too short
                        requirements.append(req_natural)
    
    return requirements


def populate_ood_csv(output_path: str, target_count: int = 300):
    """Create OOD template CSV with diverse requirements"""
    
    print(f"🔄 Populating OOD template with {target_count} requirements...")
    
    all_requirements = []
    
    # 1. Add curated requirements
    print(f"   📝 Adding {len(CURATED_REQUIREMENTS)} curated requirements...")
    for domain, req in CURATED_REQUIREMENTS:
        all_requirements.append({
            'domain_expected': domain,
            'requirement_sentence': req
        })
    
    # 2. Extract from ARFF datasets
    print(f"   📂 Extracting from ARFF datasets...")
    arff_dir = Path("Requirment_dataset")
    if arff_dir.exists():
        arff_files = list(arff_dir.glob("*.arff"))
        for arff_file in arff_files[:5]:  # Limit to 5 files
            try:
                reqs = parse_arff_requirements(arff_file)
                print(f"      {arff_file.name}: {len(reqs)} requirements")
                for req in reqs[:40]:  # Max 40 per file
                    all_requirements.append({
                        'domain_expected': 'general',
                        'requirement_sentence': req
                    })
            except Exception as e:
                print(f"      ⚠️  Error reading {arff_file.name}: {e}")
    
    # 3. Trim to target count
    if len(all_requirements) > target_count:
        all_requirements = all_requirements[:target_count]
    
    print(f"   ✅ Total requirements collected: {len(all_requirements)}")
    
    # 4. Write CSV
    print(f"   💾 Writing to {output_path}...")
    
    fieldnames = [
        'id', 'domain_expected', 'requirement_sentence',
        'generated_title', 'generated_description', 'generated_type',
        'generated_priority', 'generated_domain', 'generated_role',
        'generated_ac_1', 'generated_ac_2', 'generated_ac_3',
        'generated_ac_4', 'generated_ac_5', 'generated_ac_6',
        'score_title_clarity', 'score_desc_correctness', 'score_ac_testability',
        'score_label_type', 'score_label_domain', 'score_priority_reasonable',
        'has_duplicates', 'notes'
    ]
    
    with open(output_path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        
        for i, req_data in enumerate(all_requirements, 1):
            row = {
                'id': i,
                'domain_expected': req_data['domain_expected'],
                'requirement_sentence': req_data['requirement_sentence'],
                # Empty fields for generation
                'generated_title': '',
                'generated_description': '',
                'generated_type': '',
                'generated_priority': '',
                'generated_domain': '',
                'generated_role': '',
                'generated_ac_1': '',
                'generated_ac_2': '',
                'generated_ac_3': '',
                'generated_ac_4': '',
                'generated_ac_5': '',
                'generated_ac_6': '',
                # Empty fields for scoring
                'score_title_clarity': '',
                'score_desc_correctness': '',
                'score_ac_testability': '',
                'score_label_type': '',
                'score_label_domain': '',
                'score_priority_reasonable': '',
                'has_duplicates': '',
                'notes': ''
            }
            writer.writerow(row)
    
    print(f"✅ OOD template populated: {output_path}")
    print(f"\n📋 Next steps:")
    print(f"   1. Review {output_path}")
    print(f"   2. Run: python scripts/eval/01_generate_ood_outputs.py {output_path} scripts/eval/ood_generated.csv --mode model")
    print(f"   3. Manually score the generated outputs")
    print(f"   4. Run: python scripts/eval/02_summarize_ood_scores.py scripts/eval/ood_generated.csv scripts/eval/ood_report.md")


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Populate OOD template')
    parser.add_argument('--output', default='scripts/eval/ood_requirements_filled.csv',
                       help='Output CSV path')
    parser.add_argument('--count', type=int, default=300,
                       help='Target number of requirements')
    
    args = parser.parse_args()
    
    populate_ood_csv(args.output, args.count)
