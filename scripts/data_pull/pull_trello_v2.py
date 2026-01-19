"""
Trello Data Puller - Optimized Version
Fetch cards from Trello boards for training data enrichment
"""
import os
import re
import json
import time
from pathlib import Path
from typing import List, Dict
from datetime import datetime
import requests
from dotenv import load_dotenv

load_dotenv()


class TrelloDataPuller:
    """Pull and normalize Trello cards"""
    
    def __init__(self, api_key: str, token: str):
        self.api_key = api_key
        self.token = token
        self.base_url = "https://api.trello.com/1"
    
    def get_board_lists(self, board_id: str) -> Dict[str, str]:
        """Get all lists for a board (fetch once, use many times)"""
        endpoint = f"{self.base_url}/boards/{board_id}/lists"
        params = {
            'key': self.api_key,
            'token': self.token,
            'fields': 'id,name'
        }
        
        try:
            response = requests.get(endpoint, params=params, timeout=30)
            response.raise_for_status()
            lists = response.json()
            
            # Build map: list_id -> list_name
            return {lst['id']: lst['name'] for lst in lists}
        except requests.exceptions.RequestException as e:
            print(f"   ⚠️  Error fetching lists from board {board_id}: {e}")
            return {}
    
    def get_board_cards(self, board_id: str) -> List[Dict]:
        """Get all cards from a Trello board"""
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
            print(f"   ❌ Error fetching cards from board {board_id}: {e}")
            return []
    
    def get_card_comments(self, card_id: str, limit: int = 5) -> List[str]:
        """Get comments for a card (optional, can be slow)"""
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
    
    def extract_acceptance_criteria(self, description: str) -> List[str]:
        """Extract checklist items or AC from description"""
        if not description:
            return []
        
        ac_list = []
        
        # Trello checklist format: - [ ] item or - [x] item
        checklist_items = re.findall(r'-\s*\[[ xX]\]\s*(.+)', description, re.IGNORECASE)
        ac_list.extend([item.strip() for item in checklist_items])
        
        # Numbered list
        numbered_items = re.findall(r'^\d+\.\s+(.+)', description, re.MULTILINE)
        ac_list.extend([item.strip() for item in numbered_items])
        
        # Bullet points (only if no checklist found)
        if not ac_list:
            bullet_items = re.findall(r'^[-*•]\s+(.+)', description, re.MULTILINE)
            ac_list.extend([item.strip() for item in bullet_items])
        
        return ac_list[:10]  # Limit to 10
    
    def infer_priority_from_labels(self, labels: List[Dict]) -> str:
        """Infer priority from label names"""
        label_names = [label.get('name', '').lower() for label in labels]
        
        # High priority keywords
        high_keywords = ['high', 'urgent', 'critical', 'blocker', 'p0', 'p1']
        if any(kw in ' '.join(label_names) for kw in high_keywords):
            return 'High'
        
        # Low priority keywords
        low_keywords = ['low', 'minor', 'nice to have', 'p3', 'p4']
        if any(kw in ' '.join(label_names) for kw in low_keywords):
            return 'Low'
        
        return 'Medium'
    
    def normalize_card(self, card: Dict, list_name: str = '', with_comments: bool = False) -> Dict:
        """Normalize Trello card to standard format"""
        # Extract AC from description
        description = card.get('desc', '').strip()
        ac_list = self.extract_acceptance_criteria(description)
        
        # Labels
        labels = card.get('labels', [])
        label_names = [label.get('name', '') for label in labels if label.get('name')]
        
        # Infer priority
        priority = self.infer_priority_from_labels(labels)
        
        # Comments (optional, can be slow)
        comments = []
        if with_comments:
            comments = self.get_card_comments(card.get('id', ''), limit=5)
        
        normalized = {
            'source': 'trello',
            'source_id': card.get('id', ''),
            'source_url': card.get('shortUrl', ''),
            'title': card.get('name', '').strip(),
            'description': description,
            'acceptance_criteria': ac_list,
            'labels': label_names,
            'components': [],  # Trello doesn't have components
            'issue_type': 'Task',  # Default type
            'priority': priority,
            'status': list_name,  # List name = status
            'resolution': 'Done' if card.get('closed', False) else '',
            'created_at': '',  # Not easily available
            'updated_at': card.get('dateLastActivity', ''),
            'comments': comments,
            'metadata': {
                'due_date': card.get('due', ''),
                'closed': card.get('closed', False)
            }
        }
        
        return normalized
    
    def pull_and_save(self, board_ids: List[str], output_file: Path, 
                     max_cards_per_board: int = 1000, with_comments: bool = False):
        """Pull cards from boards and save to JSONL"""
        print(f"\n{'='*70}")
        print(f"  TRELLO DATA PULLER")
        print(f"{'='*70}\n")
        print(f"   Boards: {len(board_ids)}")
        print(f"   Max cards per board: {max_cards_per_board}")
        print(f"   With comments: {with_comments}")
        print()
        
        all_normalized = []
        
        for idx, board_id in enumerate(board_ids, 1):
            print(f"📋 Board {idx}/{len(board_ids)}: {board_id}")
            
            # Fetch lists once for this board
            print(f"   Fetching lists...")
            lists_map = self.get_board_lists(board_id)
            print(f"   Found {len(lists_map)} lists")
            
            # Fetch cards
            print(f"   Fetching cards...")
            cards = self.get_board_cards(board_id)
            
            if not cards:
                print(f"   ⚠️  No cards found\n")
                continue
            
            # Limit
            cards = cards[:max_cards_per_board]
            print(f"   Processing {len(cards)} cards...")
            
            # Normalize
            for card in cards:
                list_id = card.get('idList', '')
                list_name = lists_map.get(list_id, '')
                
                try:
                    normalized = self.normalize_card(card, list_name, with_comments)
                    all_normalized.append(normalized)
                except Exception as e:
                    print(f"   ⚠️  Error normalizing card {card.get('id', '?')}: {e}")
            
            print(f"   ✅ Normalized {len(cards)} cards\n")
            
            # Rate limiting between boards
            if idx < len(board_ids):
                time.sleep(1)
        
        # Save
        if not all_normalized:
            print("⚠️  No cards to save")
            return
        
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            for item in all_normalized:
                f.write(json.dumps(item, ensure_ascii=False) + '\n')
        
        # Statistics
        print(f"\n{'='*70}")
        print(f"  SUMMARY")
        print(f"{'='*70}\n")
        print(f"   Total cards: {len(all_normalized)}")
        print(f"   Output: {output_file}")
        print(f"   File size: {output_file.stat().st_size / 1024:.1f} KB")
        
        # Priority distribution
        priorities = {}
        for card in all_normalized:
            p = card.get('priority', 'Medium')
            priorities[p] = priorities.get(p, 0) + 1
        
        print(f"\n   Priority distribution:")
        for p, count in sorted(priorities.items()):
            print(f"      {p}: {count}")
        
        # Cards with AC
        with_ac = sum(1 for card in all_normalized if card.get('acceptance_criteria'))
        print(f"\n   Cards with AC: {with_ac} ({with_ac/len(all_normalized)*100:.1f}%)")
        
        print(f"\n✅ Done!\n")


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Pull cards from Trello boards')
    parser.add_argument('--board-ids', help='Comma-separated board IDs')
    parser.add_argument('--output', help='Output JSONL file')
    parser.add_argument('--max-cards', type=int, default=1000,
                       help='Max cards per board')
    parser.add_argument('--with-comments', action='store_true',
                       help='Fetch comments (slower)')
    
    args = parser.parse_args()
    
    # Get credentials
    api_key = os.getenv('TRELLO_API_KEY')
    token = os.getenv('TRELLO_TOKEN')
    board_ids_str = args.board_ids or os.getenv('TRELLO_BOARD_IDS', '')
    
    if not api_key or not token:
        print("❌ Missing TRELLO_API_KEY or TRELLO_TOKEN in .env")
        exit(1)
    
    if not board_ids_str:
        print("❌ No board IDs provided (use --board-ids or TRELLO_BOARD_IDS in .env)")
        exit(1)
    
    board_ids = [bid.strip() for bid in board_ids_str.split(',') if bid.strip()]
    
    # Output file
    if args.output:
        output_file = Path(args.output)
    else:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = Path(f'data/external/trello_cards_{timestamp}.jsonl')
    
    # Pull
    puller = TrelloDataPuller(api_key, token)
    puller.pull_and_save(
        board_ids=board_ids,
        output_file=output_file,
        max_cards_per_board=args.max_cards,
        with_comments=args.with_comments
    )
