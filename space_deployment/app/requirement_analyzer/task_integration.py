"""
Mô-đun tích hợp với các công cụ quản lý task như Trello và Jira
"""

import requests
import json
import os
from typing import Dict, List, Any, Optional
import logging

logger = logging.getLogger(__name__)

class TrelloIntegration:
    """
    Tích hợp với Trello để nhập các thẻ và chuyển đổi thành tài liệu yêu cầu
    """
    
    def __init__(self, api_key: str, token: str):
        """
        Khởi tạo với API key và token của Trello
        
        Args:
            api_key: API key của Trello
            token: Token truy cập Trello
        """
        self.api_key = api_key
        self.token = token
        self.base_url = "https://api.trello.com/1"
    
    def get_board(self, board_id: str) -> Dict[str, Any]:
        """
        Lấy thông tin bảng từ Trello
        
        Args:
            board_id: ID của bảng Trello
            
        Returns:
            Dict chứa thông tin bảng
        """
        url = f"{self.base_url}/boards/{board_id}"
        params = {
            "key": self.api_key,
            "token": self.token
        }
        
        response = requests.get(url, params=params)
        response.raise_for_status()
        
        return response.json()
    
    def get_cards(self, board_id: str) -> List[Dict[str, Any]]:
        """
        Lấy tất cả các thẻ từ bảng Trello
        
        Args:
            board_id: ID của bảng Trello
            
        Returns:
            List các thẻ
        """
        url = f"{self.base_url}/boards/{board_id}/cards"
        params = {
            "key": self.api_key,
            "token": self.token
        }
        
        response = requests.get(url, params=params)
        response.raise_for_status()
        
        return response.json()
    
    def cards_to_tasks(self, cards: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Chuyển đổi thẻ Trello thành danh sách công việc
        
        Args:
            cards: List các thẻ Trello
            
        Returns:
            List các task
        """
        tasks = []
        
        for card in cards:
            # Xác định mức độ ưu tiên và độ phức tạp từ labels
            priority = "Medium"
            complexity = "Medium"
            
            for label in card.get("labels", []):
                label_name = label.get("name", "").lower()
                
                # Xác định ưu tiên
                if "high" in label_name or "urgent" in label_name or "critical" in label_name:
                    priority = "High"
                elif "low" in label_name or "minor" in label_name:
                    priority = "Low"
                
                # Xác định độ phức tạp
                if "complex" in label_name or "hard" in label_name:
                    complexity = "High"
                elif "simple" in label_name or "easy" in label_name:
                    complexity = "Low"
            
            # Tạo task
            task = {
                "title": card.get("name", ""),
                "description": card.get("desc", ""),
                "priority": priority,
                "complexity": complexity,
                "due_date": card.get("due"),
                "url": card.get("url"),
                "source": "trello"
            }
            
            tasks.append(task)
        
        return tasks
    
    def convert_to_requirements_doc(self, tasks: List[Dict[str, Any]]) -> str:
        """
        Chuyển đổi danh sách công việc thành tài liệu yêu cầu
        
        Args:
            tasks: List các task
            
        Returns:
            Văn bản yêu cầu
        """
        doc = "Software Requirements Specification\n\n"
        doc += "1. Introduction\n"
        doc += "This document contains requirements imported from Trello.\n\n"
        doc += "2. Functional Requirements\n\n"
        
        for i, task in enumerate(tasks, 1):
            doc += f"2.{i} {task['title']}\n"
            doc += f"Description: {task['description']}\n"
            doc += f"Priority: {task['priority']}\n"
            doc += f"Complexity: {task['complexity']}\n"
            if task.get('due_date'):
                doc += f"Due Date: {task['due_date']}\n"
            doc += "\n"
        
        return doc


class JiraIntegration:
    """
    Tích hợp với Jira để nhập các issue và chuyển đổi thành tài liệu yêu cầu
    """
    
    def __init__(self, base_url: str, username: str, api_token: str):
        """
        Khởi tạo với thông tin Jira
        
        Args:
            base_url: URL cơ sở của Jira (e.g., "https://your-domain.atlassian.net")
            username: Email đăng nhập Jira
            api_token: API token Jira
        """
        self.base_url = base_url.rstrip('/')
        self.auth = (username, api_token)
    
    def get_project(self, project_key: str) -> Dict[str, Any]:
        """
        Lấy thông tin dự án từ Jira
        
        Args:
            project_key: Khóa dự án Jira
            
        Returns:
            Dict chứa thông tin dự án
        """
        url = f"{self.base_url}/rest/api/3/project/{project_key}"
        
        response = requests.get(url, auth=self.auth)
        response.raise_for_status()
        
        return response.json()
    
    def get_issues(self, project_key: str, max_results: int = 100) -> List[Dict[str, Any]]:
        """
        Lấy tất cả các issue từ dự án Jira
        
        Args:
            project_key: Khóa dự án Jira
            max_results: Số lượng issue tối đa cần lấy
            
        Returns:
            List các issue
        """
        url = f"{self.base_url}/rest/api/3/search"
        params = {
            "jql": f"project = {project_key} ORDER BY created DESC",
            "maxResults": max_results
        }
        
        response = requests.get(url, params=params, auth=self.auth)
        response.raise_for_status()
        
        return response.json().get("issues", [])
    
    def issues_to_tasks(self, issues: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Chuyển đổi issue Jira thành danh sách công việc
        
        Args:
            issues: List các issue Jira
            
        Returns:
            List các task
        """
        tasks = []
        
        for issue in issues:
            fields = issue.get("fields", {})
            
            # Xác định mức độ ưu tiên
            priority = "Medium"
            priority_field = fields.get("priority", {})
            if priority_field:
                priority_name = priority_field.get("name", "").lower()
                if "high" in priority_name or "urgent" in priority_name or "critical" in priority_name:
                    priority = "High"
                elif "low" in priority_name or "minor" in priority_name or "trivial" in priority_name:
                    priority = "Low"
            
            # Xác định độ phức tạp từ story points (nếu có)
            complexity = "Medium"
            # Field chứa story points (thường là custom field)
            story_points = fields.get("customfield_10002")  # Điều chỉnh field ID nếu cần
            if story_points:
                if story_points > 8:
                    complexity = "High"
                elif story_points < 3:
                    complexity = "Low"
            
            # Tạo task
            task = {
                "title": fields.get("summary", ""),
                "description": fields.get("description", ""),
                "priority": priority,
                "complexity": complexity,
                "due_date": fields.get("duedate"),
                "url": f"{self.base_url}/browse/{issue.get('key')}",
                "source": "jira"
            }
            
            tasks.append(task)
        
        return tasks
    
    def convert_to_requirements_doc(self, tasks: List[Dict[str, Any]]) -> str:
        """
        Chuyển đổi danh sách công việc thành tài liệu yêu cầu
        
        Args:
            tasks: List các task
            
        Returns:
            Văn bản yêu cầu
        """
        doc = "Software Requirements Specification\n\n"
        doc += "1. Introduction\n"
        doc += "This document contains requirements imported from Jira.\n\n"
        doc += "2. Functional Requirements\n\n"
        
        # Phân loại các issue theo loại
        stories = [t for t in tasks if 'story' in t.get('title', '').lower() or 'user story' in t.get('description', '').lower()]
        bugs = [t for t in tasks if 'bug' in t.get('title', '').lower() or 'fix' in t.get('title', '').lower()]
        features = [t for t in tasks if t not in stories and t not in bugs]
        
        # Thêm User Stories
        if stories:
            doc += "2.1 User Stories\n\n"
            for i, task in enumerate(stories, 1):
                doc += f"2.1.{i} {task['title']}\n"
                doc += f"Description: {task['description']}\n"
                doc += f"Priority: {task['priority']}\n"
                doc += f"Complexity: {task['complexity']}\n\n"
        
        # Thêm Features
        if features:
            doc += "2.2 Features\n\n"
            for i, task in enumerate(features, 1):
                doc += f"2.2.{i} {task['title']}\n"
                doc += f"Description: {task['description']}\n"
                doc += f"Priority: {task['priority']}\n"
                doc += f"Complexity: {task['complexity']}\n\n"
        
        # Thêm Bugs/Issues
        if bugs:
            doc += "2.3 Bug Fixes\n\n"
            for i, task in enumerate(bugs, 1):
                doc += f"2.3.{i} {task['title']}\n"
                doc += f"Description: {task['description']}\n"
                doc += f"Priority: {task['priority']}\n"
                doc += f"Complexity: {task['complexity']}\n\n"
        
        return doc


# Factory function to get the appropriate integration
def get_integration(tool_type: str, **credentials) -> Optional[Any]:
    """
    Tạo đối tượng tích hợp dựa trên loại công cụ
    
    Args:
        tool_type: Loại công cụ ('trello' hoặc 'jira')
        **credentials: Thông tin xác thực cho công cụ
        
    Returns:
        Đối tượng tích hợp hoặc None nếu không hỗ trợ
    """
    if tool_type.lower() == 'trello':
        api_key = credentials.get('api_key')
        token = credentials.get('token')
        if not (api_key and token):
            raise ValueError("Trello integration requires 'api_key' and 'token'")
        return TrelloIntegration(api_key, token)
    
    elif tool_type.lower() == 'jira':
        base_url = credentials.get('base_url')
        username = credentials.get('username')
        api_token = credentials.get('api_token')
        if not (base_url and username and api_token):
            raise ValueError("Jira integration requires 'base_url', 'username', and 'api_token'")
        return JiraIntegration(base_url, username, api_token)
    
    return None
