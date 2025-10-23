
import os
import sys
from pathlib import Path
import importlib
import requests
import json

# Thêm đường dẫn gốc vào sys.path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.append(str(PROJECT_ROOT))

# Nhập module model_integration
try:
    from requirement_analyzer.model_integration import apply_weight_factors
    
    class TrelloIntegration:
        """Integration with Trello for importing project tasks"""
        
        def __init__(self, api_key, token, **kwargs):
            """
            Initialize Trello integration
            
            Args:
                api_key (str): Trello API key
                token (str): Trello token
                **kwargs: Additional arguments
            """
            self.api_key = api_key
            self.token = token
            self.base_url = "https://api.trello.com/1"
        
        def get_cards(self, board_id):
            """
            Get cards from a Trello board
            
            Args:
                board_id (str): ID of the Trello board
                
            Returns:
                list: List of cards from the board
            """
            url = f"{self.base_url}/boards/{board_id}/cards"
            params = {
                "key": self.api_key,
                "token": self.token,
                "fields": "name,desc,labels,due,idList"
            }
            
            response = requests.get(url, params=params)
            if response.status_code != 200:
                raise Exception(f"Error fetching cards: {response.text}")
                
            return response.json()
        
        def cards_to_tasks(self, cards):
            """
            Convert Trello cards to tasks
            
            Args:
                cards (list): List of Trello cards
                
            Returns:
                list: List of tasks
            """
            tasks = []
            
            for card in cards:
                # Parse card data
                task = {
                    "title": card.get("name", ""),
                    "description": card.get("desc", ""),
                    "priority": "Medium",  # Default
                    "complexity": "Medium",  # Default
                    "due_date": card.get("due", None),
                    "source_id": card.get("id", ""),
                    "source": "trello"
                }
                
                # Parse labels for priority and complexity
                labels = card.get("labels", [])
                for label in labels:
                    name = label.get("name", "").lower()
                    if "high" in name:
                        task["priority"] = "High"
                        task["complexity"] = "High"
                    elif "medium" in name:
                        task["priority"] = "Medium"
                        task["complexity"] = "Medium"
                    elif "low" in name:
                        task["priority"] = "Low"
                        task["complexity"] = "Low"
                
                tasks.append(task)
            
            return tasks
        
        def convert_to_requirements_doc(self, tasks):
            """
            Convert tasks to a requirements document
            
            Args:
                tasks (list): List of tasks
                
            Returns:
                str: Requirements document text
            """
            requirements_text = "Requirements Document\n\n"
            
            # Project overview
            requirements_text += "Project Overview:\n"
            requirements_text += f"This project consists of {len(tasks)} requirements/tasks imported from Trello.\n\n"
            
            # Add tasks
            total_complexity = 0
            for i, task in enumerate(tasks):
                title = task.get("title", f"Task {i+1}")
                description = task.get("description", "")
                priority = task.get("priority", "Medium")
                complexity = task.get("complexity", "Medium")
                
                # Convert complexity to numeric value for estimation
                complexity_value = {"Low": 1, "Medium": 2, "High": 3}.get(complexity, 2)
                total_complexity += complexity_value
                
                requirements_text += f"Requirement {i+1}: {title}\n"
                requirements_text += f"Description: {description}\n"
                requirements_text += f"Priority: {priority}\n"
                requirements_text += f"Complexity: {complexity}\n\n"
            
            # Add estimated code size based on tasks and complexity
            avg_complexity = total_complexity / len(tasks) if tasks else 2
            estimated_loc = int(len(tasks) * 500 * avg_complexity)
            requirements_text += f"\nExpected Size:\nEstimated code size: {estimated_loc} lines of code\n"
            
            return requirements_text
    
    class JiraIntegration:
        """Integration with Jira for importing project tasks"""
        
        def __init__(self, base_url, username, api_token, **kwargs):
            """
            Initialize Jira integration
            
            Args:
                base_url (str): Jira base URL
                username (str): Jira username
                api_token (str): Jira API token
                **kwargs: Additional arguments
            """
            self.base_url = base_url.rstrip('/')
            self.username = username
            self.api_token = api_token
            self.auth = (username, api_token)
        
        def get_issues(self, project_key):
            """
            Get issues from a Jira project
            
            Args:
                project_key (str): Key of the Jira project
                
            Returns:
                list: List of issues from the project
            """
            url = f"{self.base_url}/rest/api/2/search"
            query = {
                "jql": f"project={project_key}",
                "maxResults": 100,
                "fields": "summary,description,issuetype,priority,labels,components,customfield_10016"
            }
            
            response = requests.get(url, params=query, auth=self.auth)
            if response.status_code != 200:
                raise Exception(f"Error fetching issues: {response.text}")
                
            return response.json().get("issues", [])
        
        def issues_to_tasks(self, issues):
            """
            Convert Jira issues to tasks
            
            Args:
                issues (list): List of Jira issues
                
            Returns:
                list: List of tasks
            """
            tasks = []
            
            for issue in issues:
                fields = issue.get("fields", {})
                
                # Parse issue data
                task = {
                    "title": fields.get("summary", ""),
                    "description": fields.get("description", "") or "",
                    "priority": "Medium",  # Default
                    "complexity": "Medium",  # Default
                    "source_id": issue.get("id", ""),
                    "source": "jira"
                }
                
                # Parse priority
                priority = fields.get("priority", {})
                priority_name = priority.get("name", "").lower() if priority else ""
                if "high" in priority_name or "critical" in priority_name or "blocker" in priority_name:
                    task["priority"] = "High"
                elif "medium" in priority_name or "major" in priority_name:
                    task["priority"] = "Medium"
                elif "low" in priority_name or "minor" in priority_name or "trivial" in priority_name:
                    task["priority"] = "Low"
                
                # Parse complexity from story points (customfield_10016 is commonly used for story points)
                story_points = fields.get("customfield_10016")
                if story_points is not None:
                    if story_points > 8:
                        task["complexity"] = "High"
                    elif story_points > 3:
                        task["complexity"] = "Medium"
                    else:
                        task["complexity"] = "Low"
                
                tasks.append(task)
            
            return tasks
        
        def convert_to_requirements_doc(self, tasks):
            """
            Convert tasks to a requirements document
            
            Args:
                tasks (list): List of tasks
                
            Returns:
                str: Requirements document text
            """
            requirements_text = "Requirements Document\n\n"
            
            # Project overview
            requirements_text += "Project Overview:\n"
            requirements_text += f"This project consists of {len(tasks)} requirements/tasks imported from Jira.\n\n"
            
            # Add tasks
            total_complexity = 0
            for i, task in enumerate(tasks):
                title = task.get("title", f"Task {i+1}")
                description = task.get("description", "")
                priority = task.get("priority", "Medium")
                complexity = task.get("complexity", "Medium")
                
                # Convert complexity to numeric value for estimation
                complexity_value = {"Low": 1, "Medium": 2, "High": 3}.get(complexity, 2)
                total_complexity += complexity_value
                
                requirements_text += f"Requirement {i+1}: {title}\n"
                requirements_text += f"Description: {description}\n"
                requirements_text += f"Priority: {priority}\n"
                requirements_text += f"Complexity: {complexity}\n\n"
            
            # Add estimated code size based on tasks and complexity
            avg_complexity = total_complexity / len(tasks) if tasks else 2
            estimated_loc = int(len(tasks) * 500 * avg_complexity)
            requirements_text += f"\nExpected Size:\nEstimated code size: {estimated_loc} lines of code\n"
            
            return requirements_text
    
    def get_integration(integration_type, **kwargs):
        """
        Get an integration instance based on the integration type
        
        Args:
            integration_type (str): Type of integration ('trello', 'jira', etc.)
            **kwargs: Additional arguments needed for the integration
        
        Returns:
            object: An instance of the integration class
        
        Raises:
            ValueError: If the integration type is not supported
        """
        integration_map = {
            'trello': TrelloIntegration,
            'jira': JiraIntegration
        }
        
        if integration_type.lower() not in integration_map:
            raise ValueError(f"Integration type '{integration_type}' is not supported. "
                            f"Available types: {', '.join(integration_map.keys())}")
        
        integration_class = integration_map[integration_type.lower()]
        return integration_class(**kwargs)
    
    # Tích hợp vào estimator.py
    def integrate_with_estimator():
        # Đường dẫn đến file estimator.py
        estimator_path = os.path.join(PROJECT_ROOT, "requirement_analyzer", "estimator.py")
        
        # Đọc nội dung của file estimator.py
        with open(estimator_path, 'r') as f:
            lines = f.readlines()
        
        # Kiểm tra xem đã tích hợp trọng số chưa
        integrated = False
        for line in lines:
            if "apply_weight_factors" in line:
                integrated = True
                break
        
        if not integrated:
            # Tìm vị trí của method _integrated_estimate
            for i, line in enumerate(lines):
                if "def _integrated_estimate" in line:
                    method_start = i
                    break
            else:
                print("Không tìm thấy method _integrated_estimate trong estimator.py")
                return False
            
            # Tìm vị trí áp dụng trọng số
            weight_insertion_point = None
            for i in range(method_start, len(lines)):
                if "estimates = {}" in lines[i]:
                    weight_insertion_point = i + 1
                    break
            
            if weight_insertion_point is None:
                print("Không tìm thấy vị trí áp dụng trọng số trong _integrated_estimate")
                return False
            
            # Chèn code áp dụng trọng số
            weight_code = """        # Import module áp dụng trọng số nếu có
        try:
            from requirement_analyzer.model_integration import apply_weight_factors
            has_weight_module = True
        except ImportError:
            has_weight_module = False
            
"""
            lines.insert(weight_insertion_point, weight_code)
            
            # Tìm vị trí trả về kết quả
            return_point = None
            for i in range(method_start, len(lines)):
                if "return {" in lines[i]:
                    return_point = i
                    break
            
            if return_point is None:
                print("Không tìm thấy vị trí trả về kết quả trong _integrated_estimate")
                return False
            
            # Chèn code áp dụng trọng số trước khi trả về kết quả
            apply_weight_code = """        # Áp dụng trọng số nếu có module
        if has_weight_module:
            try:
                # Áp dụng các hệ số trọng số vào kết quả
                for model_name, model_result in model_results.items():
                    if isinstance(model_result, dict) and 'effort_pm' in model_result:
                        estimates[model_name] = model_result['effort_pm']
                
                # Áp dụng trọng số
                estimates = apply_weight_factors(estimates, all_params)
                
                # Cập nhật lại kết quả
                for model_name in model_results:
                    if model_name in estimates:
                        model_results[model_name]['effort_pm'] = estimates[model_name]
            except Exception as e:
                print(f"Error applying weight factors: {e}")
                
"""
            lines.insert(return_point, apply_weight_code)
            
            # Ghi lại file estimator.py
            with open(estimator_path, 'w') as f:
                f.writelines(lines)
            
            print("Đã tích hợp trọng số mô hình vào estimator.py")
            return True
        else:
            print("Đã tích hợp trọng số mô hình từ trước")
            return True
    
    if __name__ == "__main__":
        integrate_with_estimator()
except ImportError as e:
    print(f"Error importing model_integration: {e}")
    sys.exit(1)
