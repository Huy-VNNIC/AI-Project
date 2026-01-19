#!/usr/bin/env python3
"""
Pull data from Trello boards
Supports multiple boards, cards, labels, and comments
"""
import os
import sys
import json
import time
import requests
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional
import re

PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.append(str(PROJECT_ROOT))

from dotenv import load_dotenv

load_dotenv()


class TrelloDataPuller:
    """Pull cards from Trello boards"""
    
    def __init__(self, api_key: str, token: str):
        self.api_key = api_key
        self.token = token
        self.base_url = 'https://api.trello.com/1'
    
    def get_board_cards(self, board_id: str) -> List[Dict]:
        """Get all cards from a board"""
        endpoint = f"{self.base_url}/boards/{board_id}/cards"
        params = {
            'key': self.api_key,
            'token': self.token,
            'fields': 'name,desc,labels,idList,due,dateLastActivity,closed',
            'attachments': 'true',
            'members': 'true'
        }
        
        try:
            response = requests.get(endpoint, params=params, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"❌ Error fetching cards from board {board_id}: {e}")
            return []
    
    def get_card_comments(self, card_id: str, limit: int = 10) -> List[str]:
        """Get comments for a card"""
        endpoint = f"{self.base_url}/cards/{card_id}/actions"
        params = {
            'key': self.api_key,
            'token': self.token,
            'filter': 'commentCard',
            'limit': limit
        }
        
        try:
            response = requests.get(endpoint, params=params, timeout=10)
            response.raise_for_status()
            actions = response.json()
            
            comments = []
            for action in actions:
                text = action.get('data', {}).get('text', '')
                if text:
                    comments.append(text.strip())
            
            return comments
        except:
            return []
    
    def get_list_name(self, board_id: str, list_id: str) -> str:
        """Get list name"""
        endpoint = f"{self.base_url}/lists/{list_id}"
        params = {
            'key': self.api_key,
            'token': self.token,
            'fields': 'name'
        }
        
        try:
            response = requests.get(endpoint, params=params, timeout=10)
            response.raise_for_status()
            return response.json().get('name', '')
        except:
            return ''
    
    def extract_acceptance_criteria(self, description: str) -> List[str]:
        """Extract checklist items or AC from description"""
        if not description:
            return []
        
        ac_list = []
        
        # Trello checklist format: - [ ] item or - [x] item
        checklist_items = re.findall(r'-\s*\[[ x]\]\s*(.+)', description, re.IGNORECASE)
        ac_list.extend([item.strip() for item in checklist_items])
        
        # Numbered list
        numbered_items = re.findall(r'\d+\.\s+(.+)', description)
        ac_list.extend([item.strip() for item in numbered_items])
        
        # Bullet points
        bullet_items = re.findall(r'[-*•]\s+(.+)', description)
        if not ac_list:  # Only if no checklist found
            ac_list.extend([item.strip() for item in bullet_items])
        
        return ac_list[:10]  # Limit to 10
    
    def normalize_card(self, card: Dict, board_id: str) -> Dict:
        """Normalize Trello card to standard format"""
        # Get list name (status)
        list_id = card.get('idList', '')
        list_name = self.get_list_name(board_id, list_id) if list_id else ''
        
        # Extract AC from description
        description = card.get('desc', '').strip()
        ac_list = self.extract_acceptance_criteria(description)
        
        # Labels
        labels = [label.get('name', label.get('color', '')) 
                 for label in card.get('labels', [])]
        labels = [l for l in labels if l]  # Remove empty
        
        # Get comments (optional)
        card_id = card.get('id', '')
        comments = self.get_card_comments(card_id, limit=5) if card_id else []
        
        # Map to priority (heuristic from labels)
        priority = 'Medium'  # Default
        label_text = ' '.join(labels).lower()
        if any(word in label_text for word in ['high', 'urgent', 'critical', 'p1']):
            priority = 'High'
        elif any(word in label_text for word in ['low', 'minor', 'p3']):
            priority = 'Low'
        
        normalized = {
            'source': 'trello',
            'source_id': card.get('id', ''),
            'source_url': card.get('url', ''),
            'title': card.get('name', '').strip(),
            'description': description,
            'acceptance_criteria': ac_list,
            'labels': labels,
            'components': [list_name] if list_name else [],
            'issue_type': 'Task',  # Trello doesn't have types
            'priority': priority,
            'status': list_name,
            'resolution': 'Done' if card.get('closed') else '',
            'created_at': card.get('dateLastActivity', ''),  # Trello doesn't expose created
            'updated_at': card.get('dateLastActivity', ''),
            'comments': comments,
            'metadata': {
                'board_id': board_id,
                'list_id': list_id,
                'due': card.get('due', ''),
                'closed': card.get('closed', False)
            }
        }
        
        return normalized
    
    def pull_and_save(self, board_ids: List[str], output_file: Path):
        """Pull cards from multiple boards and save"""
        print(f"\n{'='*70}")
        print(f"  TRELLO DATA PULLER")
        print(f"{'='*70}\n")
        
        all_normalized = []
        
        for board_id in board_ids:
            print(f"📋 Fetching cards from board: {board_id}")
            cards = self.get_board_cards(board_id)
            
            if not cards:
                print(f"   ⚠️  No cards found")
                continue
            
            print(f"   Found {len(cards)} cards")
            
            # Normalize
            for card in cards:
                try:
                    if not card.get('closed', False):  # Skip archived
                        norm = self.normalize_card(card, board_id)
                        if norm['title'] and len(norm['title']) > 3:
                            all_normalized.append(norm)
                except Exception as e:
                    print(f"   ⚠️  Error normalizing card: {e}")
            
            time.sleep(1)  # Rate limiting
        
        if not all_normalized:
            print("\n⚠️  No cards to save")
            return
        
        # Save
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            for item in all_normalized:
                f.write(json.dumps(item, ensure_ascii=False) + '\n')
        
        print(f"\n✅ Saved {len(all_normalized)} cards to: {output_file}")
        
        # Stats
        print(f"\n📊 Statistics:")
        print(f"   Total cards: {len(all_normalized)}")
        print(f"   With descriptions: {sum(1 for x in all_normalized if x['description'])}")
        print(f"   With AC/checklists: {sum(1 for x in all_normalized if x['acceptance_criteria'])}")
        
        statuses = {}
        for item in all_normalized:
            status = item['status']
            statuses[status] = statuses.get(status, 0) + 1
        
        print(f"\n   Lists (status):")
        for status, count in sorted(statuses.items(), key=lambda x: -x[1]):
            print(f"     {status}: {count}")


def main():
    # Load config
    api_key = os.getenv('TRELLO_API_KEY')
    token = os.getenv('TRELLO_TOKEN')
    board_ids_str = os.getenv('TRELLO_BOARD_IDS', '')
    
    if not all([api_key, token, board_ids_str]):
        print("❌ Missing Trello credentials in .env file")
        print("\nPlease set:")
        print("  TRELLO_API_KEY")
        print("  TRELLO_TOKEN")
        print("  TRELLO_BOARD_IDS")
        print("\nGet your key and token from: https://trello.com/app-key")
        return 1
    
    board_ids = [bid.strip() for bid in board_ids_str.split(',') if bid.strip()]
    
    if not board_ids:
        print("❌ No board IDs provided")
        return 1
    
    # Output file
    output_dir = Path(os.getenv('DATA_OUTPUT_DIR', 'data/external'))
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_file = output_dir / f'trello_cards_{timestamp}.jsonl'
    
    # Pull
    puller = TrelloDataPuller(api_key, token)
    puller.pull_and_save(board_ids, output_file)
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
