#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import requests
import re

url = "http://127.0.0.1:8000/task_Invest"

# Form data with Vietnamese text
data = {
    "text": "Xây dựng toàn bộ hệ thống quản lý dự án Agile",
    "split_mode": "line",
    "min_length": "15",
    "input_mode": "text"
}

print("="*60)
print("TEST: Form Endpoint /task_Invest")
print("="*60)
print(f"Input: {data['text']}")
print()

try:
    response = requests.post(url, data=data, timeout=10)
    print(f"Status: {response.status_code}")
    
    # Look for task count in HTML
    # Pattern from template: <div class="fs-2 fw-bold" id="sumCount">{{ analysis_data.summary.task_count}}</div>
    match_count = re.search(r'<div class="fs-2 fw-bold" id="sumCount">(\d+)</div>', response.text)
    if match_count:
        task_count = int(match_count.group(1))
        print(f"Task count displayed: {task_count}")
    else:
        print("Could not find task count in HTML")
        task_count = None
    
    # Look for average score display
    # Pattern: <div class="fs-2 fw-bold" id="sumAvg">0.8889</div>
    match_score = re.search(r'<div class="fs-2 fw-bold" id="sumAvg">([\d.]+)</div>', response.text)
    if match_score:
        avg_score = float(match_score.group(1))
        print(f"Average score displayed: {avg_score}")
    else:
        print("Could not find average score in HTML")
    
    # Count task-card elements
    task_cards = response.text.count('class="card task-card"')
    print(f"Task cards in HTML: {task_cards}")
    
    # Look for the three task titles
    if "Tạo API CRUD Project" in response.text:
        print("✓ Found task 1: Tạo API CRUD Project")
    if "Tạo API CRUD Task" in response.text:
        print("✓ Found task 2: Tạo API CRUD Task")
    if "Hiển thị Kanban board" in response.text:
        print("✓ Found task 3: Hiển thị Kanban board")
    
    print()
    if task_count == 3 and task_cards == 3:
        print("✓ SUCCESS: FE displaying 3 tasks correctly!")
    else:
        print(f"✗ WARNING: Task count={task_count}, Task cards={task_cards}")

except Exception as e:
    print(f"Error: {e}")
