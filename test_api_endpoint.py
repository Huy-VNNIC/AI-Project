#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import requests
import json

url = "http://127.0.0.1:8000/api/task-invest/analyze-form"

# Form data with Vietnamese text
data = {
    "text": "Xây dựng toàn bộ hệ thống quản lý dự án Agile",
    "split_mode": "line",
    "min_length": "15",
    "input_mode": "text"
}

print("="*60)
print("TEST: API Endpoint /api/task-invest/analyze-form")
print("="*60)
print(f"Input: {data['text']}")
print()

try:
    response = requests.post(url, data=data, timeout=10)
    print(f"Status: {response.status_code}")
    
    if response.headers.get('content-type', '').startswith('application/json'):
        result = response.json()
        
        task_count = result.get('summary', {}).get('task_count', 0)
        avg_score = result.get('summary', {}).get('average_score', 0)
        
        print(f"Task count: {task_count}")
        print(f"Average score: {avg_score}")
        
        results = result.get('results', [])
        print(f"Results array length: {len(results)}")
        print()
        
        if len(results) > 0:
            print("Tasks:")
            for i, task in enumerate(results, 1):
                title = task.get('title', 'N/A')
                score = task.get('score', 0)
                print(f"  {i}. {title} (score: {score})")
        
        if task_count == 3:
            print("\n✓ SUCCESS: API returned 3 tasks!")
        else:
            print(f"\n✗ FAILED: Expected 3 tasks, got {task_count}")
    else:
        print(f"Content-Type: {response.headers.get('content-type')}")
        print("Response is not JSON")

except Exception as e:
    print(f"Error: {e}")
