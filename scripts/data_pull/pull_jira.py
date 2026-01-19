#!/usr/bin/env python3
"""
Pull data from Jira (Atlassian Cloud/Server)
Supports pagination, ADF->text conversion, and structured output
"""
import os
import sys
import json
import time
import hashlib
import requests
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional
from urllib.parse import urljoin
import html
import re

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.append(str(PROJECT_ROOT))

from dotenv import load_dotenv

load_dotenv()


class JiraDataPuller:
    """Pull issues from Jira with proper authentication and pagination"""
    
    def __init__(self, base_url: str, email: str, api_token: str):
        self.base_url = base_url.rstrip('/')
        self.email = email
        self.api_token = api_token
        self.session = requests.Session()
        self.session.auth = (email, api_token)
        self.session.headers.update({
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        })
    
    def search_issues(self, jql: str, max_results: int = 100, 
                     fields: Optional[List[str]] = None) -> List[Dict]:
        """Search Jira issues with pagination"""
        if fields is None:
            fields = [
                'summary', 'description', 'issuetype', 'priority', 
                'labels', 'components', 'created', 'updated', 
                'status', 'resolution', 'comment',
                'project', 'reporter', 'assignee'
            ]
        
        all_issues = []
        start_at = 0
        
        print(f"🔍 Searching Jira with JQL: {jql}")
        
        while True:
            endpoint = urljoin(self.base_url, '/rest/api/3/search')
            params = {
                'jql': jql,
                'startAt': start_at,
                'maxResults': max_results,
                'fields': ','.join(fields)
            }
            
            try:
                response = self.session.get(endpoint, params=params, timeout=30)
                response.raise_for_status()
                data = response.json()
                
                issues = data.get('issues', [])
                total = data.get('total', 0)
                
                if not issues:
                    break
                
                all_issues.extend(issues)
                start_at += len(issues)
                
                print(f"   Retrieved {len(all_issues)}/{total} issues...", end='\r')
                
                if start_at >= total:
                    break
                
                time.sleep(0.5)  # Rate limiting
                
            except requests.exceptions.RequestException as e:
                print(f"\n❌ Error fetching issues: {e}")
                break
        
        print(f"\n✅ Total issues retrieved: {len(all_issues)}")
        return all_issues
    
    def adf_to_text(self, adf_content: Dict) -> str:
        """Convert Atlassian Document Format to plain text"""
        if not adf_content or not isinstance(adf_content, dict):
            return ""
        
        def extract_text(node):
            texts = []
            
            if isinstance(node, dict):
                # Text node
                if node.get('type') == 'text':
                    texts.append(node.get('text', ''))
                
                # Recursive for content
                if 'content' in node:
                    for child in node['content']:
                        texts.append(extract_text(child))
                
                # Handle other types
                if node.get('type') in ['paragraph', 'listItem', 'tableCell']:
                    texts.append('\n')
            
            elif isinstance(node, list):
                for item in node:
                    texts.append(extract_text(item))
            
            return ' '.join(texts)
        
        text = extract_text(adf_content)
        # Clean up multiple spaces/newlines
        text = re.sub(r'\s+', ' ', text).strip()
        return text
    
    def extract_acceptance_criteria(self, description: str) -> List[str]:
        """Extract acceptance criteria from description"""
        if not description:
            return []
        
        # Common patterns for AC
        ac_patterns = [
            r'acceptance criteria[:\s]+(.+?)(?=\n\n|\Z)',
            r'AC[:\s]+(.+?)(?=\n\n|\Z)',
            r'criteria[:\s]+(.+?)(?=\n\n|\Z)',
        ]
        
        ac_list = []
        for pattern in ac_patterns:
            matches = re.findall(pattern, description, re.IGNORECASE | re.DOTALL)
            if matches:
                # Split by bullet points or numbers
                for match in matches:
                    items = re.split(r'\n[-*•\d]+\.?\s+', match)
                    ac_list.extend([item.strip() for item in items if item.strip()])
        
        return ac_list[:10]  # Limit to 10 AC
    
    def clean_html(self, text: str) -> str:
        """Remove HTML tags and decode entities"""
        if not text:
            return ""
        text = html.unescape(text)
        text = re.sub(r'<[^>]+>', '', text)
        text = re.sub(r'\s+', ' ', text).strip()
        return text
    
    def normalize_issue(self, issue: Dict) -> Dict:
        """Normalize Jira issue to standard format"""
        fields = issue.get('fields', {})
        
        # Description handling (ADF or plain text)
        description_raw = fields.get('description')
        if isinstance(description_raw, dict):
            description = self.adf_to_text(description_raw)
        elif isinstance(description_raw, str):
            description = self.clean_html(description_raw)
        else:
            description = ""
        
        # Extract AC
        ac_list = self.extract_acceptance_criteria(description)
        
        # Components
        components = [c.get('name', '') for c in fields.get('components', [])]
        
        # Comments (optional)
        comments = []
        comment_data = fields.get('comment', {})
        if isinstance(comment_data, dict):
            for comment in comment_data.get('comments', [])[:5]:  # Limit to 5
                body = comment.get('body')
                if isinstance(body, dict):
                    text = self.adf_to_text(body)
                elif isinstance(body, str):
                    text = self.clean_html(body)
                else:
                    text = ""
                if text:
                    comments.append(text)
        
        # Safe metadata access
        project = fields.get('project', {})
        reporter = fields.get('reporter', {})
        assignee = fields.get('assignee', {})
        
        normalized = {
            'source': 'jira',
            'source_id': issue.get('key', ''),
            'source_url': f"{self.base_url}/browse/{issue.get('key', '')}",
            'title': fields.get('summary', '').strip(),
            'description': description,
            'acceptance_criteria': ac_list,
            'labels': fields.get('labels', []),
            'components': components,
            'issue_type': fields.get('issuetype', {}).get('name', ''),
            'priority': fields.get('priority', {}).get('name', ''),
            'status': fields.get('status', {}).get('name', ''),
            'resolution': fields.get('resolution', {}).get('name', '') if fields.get('resolution') else '',
            'created_at': fields.get('created', ''),
            'updated_at': fields.get('updated', ''),
            'comments': comments,
            'metadata': {
                'project': project.get('key', '') if isinstance(project, dict) else '',
                'reporter': reporter.get('displayName', '') if isinstance(reporter, dict) else '',
                'assignee': assignee.get('displayName', '') if isinstance(assignee, dict) and assignee else ''
            }
        }
        
        return normalized
    
    def pull_and_save(self, jql: str, output_file: Path, max_issues: int = 10000):
        """Pull issues and save to JSONL"""
        print(f"\n{'='*70}")
        print(f"  JIRA DATA PULLER")
        print(f"{'='*70}\n")
        
        # Search issues
        raw_issues = self.search_issues(jql, max_results=100)
        
        if not raw_issues:
            print("⚠️  No issues found")
            return
        
        # Limit
        raw_issues = raw_issues[:max_issues]
        
        # Normalize
        print(f"\n📝 Normalizing {len(raw_issues)} issues...")
        normalized = []
        for issue in raw_issues:
            try:
                norm = self.normalize_issue(issue)
                if norm['title'] and len(norm['title']) > 3:  # Quality filter
                    normalized.append(norm)
            except Exception as e:
                print(f"⚠️  Error normalizing {issue.get('key')}: {e}")
        
        # Save
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            for item in normalized:
                f.write(json.dumps(item, ensure_ascii=False) + '\n')
        
        print(f"\n✅ Saved {len(normalized)} issues to: {output_file}")
        
        # Stats
        print(f"\n📊 Statistics:")
        print(f"   Total issues: {len(normalized)}")
        print(f"   With descriptions: {sum(1 for x in normalized if x['description'])}")
        print(f"   With AC: {sum(1 for x in normalized if x['acceptance_criteria'])}")
        
        issue_types = {}
        for item in normalized:
            it = item['issue_type']
            issue_types[it] = issue_types.get(it, 0) + 1
        
        print(f"\n   Issue types:")
        for it, count in sorted(issue_types.items(), key=lambda x: -x[1]):
            print(f"     {it}: {count}")


def main():
    # Load config
    base_url = os.getenv('JIRA_BASE_URL')
    email = os.getenv('JIRA_EMAIL')
    api_token = os.getenv('JIRA_API_TOKEN')
    jql = os.getenv('JIRA_JQL', 'created >= -365d')
    
    if not all([base_url, email, api_token]):
        print("❌ Missing Jira credentials in .env file")
        print("\nPlease set:")
        print("  JIRA_BASE_URL")
        print("  JIRA_EMAIL")
        print("  JIRA_API_TOKEN")
        print("\nCopy .env.example to .env and fill in your credentials")
        return 1
    
    # Output file
    output_dir = Path(os.getenv('DATA_OUTPUT_DIR', 'data/external'))
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_file = output_dir / f'jira_issues_{timestamp}.jsonl'
    
    # Pull
    puller = JiraDataPuller(base_url, email, api_token)
    puller.pull_and_save(jql, output_file)
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
