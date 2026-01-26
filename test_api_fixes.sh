#!/bin/bash
# Quick test for fixed API endpoints

echo "=================================="
echo "Testing Task Generation API Fixes"
echo "=================================="

# Test 1: Status endpoint
echo ""
echo "Test 1: Check API status..."
curl -s http://localhost:8000/api/task-generation/status | python3 -m json.tool

# Test 2: Simple generation
echo ""
echo ""
echo "Test 2: Generate task from simple text..."
curl -s -X POST "http://localhost:8000/api/task-generation/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "The system must allow users to login with email and password."
  }' | python3 -c "import sys, json; data=json.load(sys.stdin); print(f\"✅ Generated {len(data['tasks'])} task(s)\"); print(f\"   Title: {data['tasks'][0]['title'] if data['tasks'] else 'N/A'}\")"

# Test 3: With threshold parameter
echo ""
echo "Test 3: Generate with custom threshold..."
curl -s -X POST "http://localhost:8000/api/task-generation/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "The system must allow users to login with email and password. Users should be able to reset their password.",
    "max_tasks": 10,
    "requirement_threshold": 0.3
  }' | python3 -c "import sys, json; data=json.load(sys.stdin); print(f\"✅ Generated {len(data['tasks'])} task(s) with threshold=0.3\")"

echo ""
echo "=================================="
echo "All tests completed!"
echo "=================================="
