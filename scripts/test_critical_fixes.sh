#!/bin/bash
# Test critical fixes for h11 error and file upload

set -e

echo "================================================"
echo "Testing Critical Bug Fixes"
echo "================================================"

# Test 1: Favicon endpoint (h11 fix)
echo ""
echo "TEST 1: Favicon endpoint (no h11 crash)"
echo "-----------------------------------------------"
# Use -v to get headers with GET request
response=$(curl -s -v http://localhost:8000/favicon.ico 2>&1)
status_code=$(echo "$response" | grep "< HTTP" | awk '{print $3}')

# Check it's an icon file
file_type=$(curl -s http://localhost:8000/favicon.ico | file -)

echo "Status: $status_code"
echo "File type: $file_type"

if [ "$status_code" = "200" ]; then
    echo "✓ Status: 200 OK"
else
    echo "✗ FAIL: Expected 200, got $status_code"
    exit 1
fi

if [[ "$file_type" == *"icon"* ]] || [[ "$file_type" == *"PNG"* ]]; then
    echo "✓ Returns valid icon/image file"
else
    echo "✗ FAIL: Not an icon file: $file_type"
    exit 1
fi

# Test 2: File upload with 57 requirements
echo ""
echo "TEST 2: File upload - should generate many tasks from 57 requirements"
echo "-----------------------------------------------"

# Create test file with 57 requirements
cat > /tmp/test_requirements.md << 'EOF'
# Hotel Management System Requirements

## User Authentication
1. The system shall allow users to register with email and password
2. The system shall validate email format during registration
3. The system shall send verification emails to new users
4. The system shall allow users to login with credentials
5. The system shall implement password hashing for security
6. The system shall provide password reset functionality
7. The system shall lock accounts after 5 failed login attempts

## Booking Management
8. The system shall display available rooms by date range
9. The system shall allow guests to select room type
10. The system shall calculate total price including taxes
11. The system shall process credit card payments
12. The system shall generate booking confirmation numbers
13. The system shall send booking confirmations via email
14. The system shall allow users to modify existing bookings
15. The system shall apply cancellation policies
16. The system shall process refunds for cancelled bookings

## Room Management
17. The system shall maintain room inventory by type
18. The system shall update room status (available, occupied, maintenance)
19. The system shall track room amenities and features
20. The system shall assign rooms to bookings automatically
21. The system shall handle room upgrades and downgrades
22. The system shall prevent double-booking of rooms

## Guest Services
23. The system shall record guest preferences and special requests
24. The system shall manage concierge service requests
25. The system shall track loyalty program points
26. The system shall provide digital key access
27. The system shall allow early check-in requests
28. The system shall allow late checkout requests

## Staff Management
29. The system shall maintain employee records
30. The system shall track staff schedules and shifts
31. The system shall assign tasks to housekeeping staff
32. The system shall record maintenance requests
33. The system shall track employee performance metrics

## Reporting
34. The system shall generate occupancy reports
35. The system shall generate revenue reports by period
36. The system shall provide guest satisfaction analytics
37. The system shall track booking sources and channels
38. The system shall export reports in PDF and Excel formats

## Integration
39. The system shall integrate with payment gateways
40. The system shall sync with property management systems
41. The system shall connect to email service providers
42. The system shall integrate with SMS notification services
43. The system shall support calendar feed exports

## Notifications
44. The system shall send booking reminders 24 hours before check-in
45. The system shall notify staff of new bookings
46. The system shall alert guests of room ready status
47. The system shall send checkout reminders
48. The system shall notify managers of cancellations

## Security
49. The system shall encrypt sensitive guest data
50. The system shall log all administrative actions
51. The system shall implement role-based access control
52. The system shall comply with PCI-DSS for payment data
53. The system shall perform regular security audits
54. The system shall implement 2FA for admin accounts

## Performance
55. The system shall support 1000 concurrent users
56. The system shall respond to search queries within 2 seconds
57. The system shall maintain 99.9% uptime
EOF

# Call API
echo "Uploading file with 57 requirements..."
response=$(curl -s -X POST \
  http://localhost:8000/api/task-generation/generate-from-file \
  -F "file=@/tmp/test_requirements.md" \
  -F "max_tasks=200" \
  -F "requirement_threshold=0.3")

# Parse response
total_tasks=$(echo "$response" | python3 -c "import sys, json; print(json.load(sys.stdin)['total_tasks'])" 2>/dev/null || echo "0")
method=$(echo "$response" | python3 -c "import sys, json; print(json.load(sys.stdin)['ingestion']['method'])" 2>/dev/null || echo "unknown")
reqs_extracted=$(echo "$response" | python3 -c "import sys, json; print(json.load(sys.stdin)['ingestion']['requirements_extracted'])" 2>/dev/null || echo "0")

echo "Results:"
echo "  Requirements extracted: $reqs_extracted/57"
echo "  Tasks generated: $total_tasks"
echo "  Method: $method"

if [ "$reqs_extracted" -ge "50" ]; then
    echo "✓ Extracted most requirements (≥50)"
else
    echo "✗ FAIL: Only extracted $reqs_extracted requirements (expected ≥50)"
    exit 1
fi

if [ "$total_tasks" -ge "15" ]; then
    echo "✓ Generated significant tasks (≥15)"
else
    echo "✗ FAIL: Only generated $total_tasks tasks (expected ≥15)"
    exit 1
fi

if [[ "$method" == *"bypass"* ]] || [[ "$method" == *"generate_from_sentences"* ]]; then
    echo "✓ Using bypass segmenter method"
else
    echo "⚠ WARNING: Method is '$method' (expected bypass segmenter)"
fi

echo ""
echo "================================================"
echo "✅ ALL TESTS PASSED"
echo "================================================"
