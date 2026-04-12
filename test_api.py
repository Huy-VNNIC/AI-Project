import requests
import json

# Test the API endpoint
url = "http://127.0.0.1:8000/task_Invest"

# Form data with the large Agile task
data = {
    "text": "Xay dung toan bo he thong quan ly du an Agile",  # ASCII version to avoid encoding issues
    "split_mode": "line",
    "min_length": "15",
    "input_mode": "text"
}

# Make the POST request
response = requests.post(url, data=data)

print(f"Status Code: {response.status_code}")
print(f"Response Type: {response.headers.get('content-type')}")

# Check if it's JSON or HTML
if "application/json" in response.headers.get('content-type', ''):
    result = response.json()
    print(f"\nJSON Response:")
    print(json.dumps(result, indent=2))
elif "text/html" in response.headers.get('content-type', ''):
    # Extract analysis data from HTML (check if we can find the number of tasks)
    if "sumCount" in response.text:
        print("\nHTML Response contains analysis data")
        # Try to find the task count
        lines = response.text.split('\n')
        for i, line in enumerate(lines):
            if 'sumCount' in line or 'task_count' in line:
                print(f"Found at line {i}: {line[:100]}")
    else:
        print("\nHTML Response (no analysis data found)")
