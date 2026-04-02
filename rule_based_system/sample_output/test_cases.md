# Test Cases Report
**Total Test Cases:** 53

---
## Requirement: REQ_95D65E

### [Positive] User logins email with valid inputs
- **Test ID:** TC_B62E19
- **Type:** positive
- **Priority:** high
- **Precondition:** User is registered and on the login/home page
- **Steps:**
  1. Navigate to login page / feature
  1. Enter valid email: 'user@example.com'
  1. Enter valid password: 'StrongPass@123'
  1. Submit / Execute login
- **Expected Result:** can login with email and password
 2.

### [Negative] User logins email — invalid email
- **Test ID:** TC_2285C3
- **Type:** negative
- **Priority:** high
- **Precondition:** User is registered and on the login/home page
- **Steps:**
  1. Navigate to login page
  1. Enter invalid email: 'not-an-email'
  1. Submit/proceed
- **Expected Result:** System shows error: invalid email

### [Negative] User logins email — invalid password
- **Test ID:** TC_25120C
- **Type:** negative
- **Priority:** high
- **Precondition:** User is registered and on the login/home page
- **Steps:**
  1. Navigate to login page
  1. Enter invalid password: 'weak'
  1. Submit/proceed
- **Expected Result:** System shows error: invalid password

### [Edge] User logins email — empty email
- **Test ID:** TC_FA2FF8
- **Type:** edge
- **Priority:** medium
- **Precondition:** User is registered and on the login/home page
- **Steps:**
  1. Navigate to login page
  1. Leave email empty
  1. Submit/proceed
- **Expected Result:** System shows required field error for email

### [Edge] User logins email — boundary email
- **Test ID:** TC_48C3F8
- **Type:** edge
- **Priority:** low
- **Precondition:** User is registered and on the login/home page
- **Steps:**
  1. Navigate to login page
  1. Enter boundary value for email: 'a@b.c'
  1. Submit/proceed
- **Expected Result:** System handles boundary value correctly

### [Edge] User logins email — empty password
- **Test ID:** TC_CCD37C
- **Type:** edge
- **Priority:** medium
- **Precondition:** User is registered and on the login/home page
- **Steps:**
  1. Navigate to login page
  1. Leave password empty
  1. Submit/proceed
- **Expected Result:** System shows required field error for password

### [Edge] User logins email — boundary password
- **Test ID:** TC_E4825A
- **Type:** edge
- **Priority:** low
- **Precondition:** User is registered and on the login/home page
- **Steps:**
  1. Navigate to login page
  1. Enter boundary value for password: 'A1!'
  1. Submit/proceed
- **Expected Result:** System handles boundary value correctly

### [Security] User logins email — SQL injection attempt
- **Test ID:** TC_67B23A
- **Type:** security
- **Priority:** high
- **Precondition:** User is registered and on the login/home page
- **Steps:**
  1. Navigate to the relevant input form
  1. Enter SQL injection payload: ' OR '1'='1
  1. Submit the form
- **Expected Result:** System sanitizes input, shows error or rejects request. No data exposed.

### [Security] User logins email — XSS attempt
- **Test ID:** TC_7F0455
- **Type:** security
- **Priority:** high
- **Precondition:** User is registered and on the login/home page
- **Steps:**
  1. Navigate to the relevant input form
  1. Enter XSS payload: <script>alert('xss')</script>
  1. Submit the form
- **Expected Result:** System escapes or rejects malicious script. No script executes.

### [Security] User logins email — brute force attempt
- **Test ID:** TC_034C2C
- **Type:** security
- **Priority:** high
- **Precondition:** System is accessible
- **Steps:**
  1. Attempt login with wrong password 10+ times
  1. Check system response after repeated failures
- **Expected Result:** System locks account or introduces delay after N failed attempts


---

## Requirement: REQ_B2FAF6

### [Positive] System validates format & email format with valid inputs
- **Test ID:** TC_77E005
- **Type:** positive
- **Priority:** medium
- **Precondition:** System is running and accessible
- **Steps:**
  1. Navigate to validate page / feature
  1. Enter valid format: 'valid input'
  1. Enter valid email format: 'valid input'
  1. Submit / Execute validate
- **Expected Result:** must validate email format
 3.

### [Negative] System validates format & email format — invalid format
- **Test ID:** TC_11C69A
- **Type:** negative
- **Priority:** medium
- **Precondition:** System is running and accessible
- **Steps:**
  1. Navigate to validate page
  1. Enter invalid format: 'invalid input'
  1. Submit/proceed
- **Expected Result:** System shows error: invalid format

### [Negative] System validates format & email format — invalid email format
- **Test ID:** TC_C742C1
- **Type:** negative
- **Priority:** medium
- **Precondition:** System is running and accessible
- **Steps:**
  1. Navigate to validate page
  1. Enter invalid email format: 'invalid input'
  1. Submit/proceed
- **Expected Result:** System shows error: invalid email format

### [Edge] System validates format & email format — empty format
- **Test ID:** TC_2DBD3B
- **Type:** edge
- **Priority:** medium
- **Precondition:** System is running and accessible
- **Steps:**
  1. Navigate to validate page
  1. Leave format empty
  1. Submit/proceed
- **Expected Result:** System shows required field error for format

### [Edge] System validates format & email format — boundary format
- **Test ID:** TC_9EE4D4
- **Type:** edge
- **Priority:** low
- **Precondition:** System is running and accessible
- **Steps:**
  1. Navigate to validate page
  1. Enter boundary value for format: 'boundary value'
  1. Submit/proceed
- **Expected Result:** System handles boundary value correctly

### [Edge] System validates format & email format — empty email format
- **Test ID:** TC_C6FA3C
- **Type:** edge
- **Priority:** medium
- **Precondition:** System is running and accessible
- **Steps:**
  1. Navigate to validate page
  1. Leave email format empty
  1. Submit/proceed
- **Expected Result:** System shows required field error for email format

### [Edge] System validates format & email format — boundary email format
- **Test ID:** TC_ACB20B
- **Type:** edge
- **Priority:** low
- **Precondition:** System is running and accessible
- **Steps:**
  1. Navigate to validate page
  1. Enter boundary value for email format: 'boundary value'
  1. Submit/proceed
- **Expected Result:** System handles boundary value correctly


---

## Requirement: REQ_5820E1

### [Positive] Login shows message & error message with valid inputs
- **Test ID:** TC_E25F0B
- **Type:** positive
- **Priority:** high
- **Precondition:** if login fails
- **Steps:**
  1. Navigate to show page / feature
  1. Enter valid message: 'valid input'
  1. Enter valid error message: 'valid input'
  1. Submit / Execute show
- **Expected Result:** If login fails, display error message
 4.

### [Negative] Login shows message & error message — invalid message
- **Test ID:** TC_BBBCE5
- **Type:** negative
- **Priority:** high
- **Precondition:** if login fails
- **Steps:**
  1. Navigate to show page
  1. Enter invalid message: 'invalid input'
  1. Submit/proceed
- **Expected Result:** System shows error: invalid message

### [Negative] Login shows message & error message — invalid error message
- **Test ID:** TC_26F815
- **Type:** negative
- **Priority:** high
- **Precondition:** if login fails
- **Steps:**
  1. Navigate to show page
  1. Enter invalid error message: 'invalid input'
  1. Submit/proceed
- **Expected Result:** System shows error: invalid error message

### [Edge] Login shows message & error message — empty message
- **Test ID:** TC_9F9DA8
- **Type:** edge
- **Priority:** medium
- **Precondition:** if login fails
- **Steps:**
  1. Navigate to show page
  1. Leave message empty
  1. Submit/proceed
- **Expected Result:** System shows required field error for message

### [Edge] Login shows message & error message — boundary message
- **Test ID:** TC_F74A2A
- **Type:** edge
- **Priority:** low
- **Precondition:** if login fails
- **Steps:**
  1. Navigate to show page
  1. Enter boundary value for message: 'boundary value'
  1. Submit/proceed
- **Expected Result:** System handles boundary value correctly

### [Edge] Login shows message & error message — empty error message
- **Test ID:** TC_602442
- **Type:** edge
- **Priority:** medium
- **Precondition:** if login fails
- **Steps:**
  1. Navigate to show page
  1. Leave error message empty
  1. Submit/proceed
- **Expected Result:** System shows required field error for error message

### [Edge] Login shows message & error message — boundary error message
- **Test ID:** TC_67AC88
- **Type:** edge
- **Priority:** low
- **Precondition:** if login fails
- **Steps:**
  1. Navigate to show page
  1. Enter boundary value for error message: 'boundary value'
  1. Submit/proceed
- **Expected Result:** System handles boundary value correctly

### [Condition] Login shows message & error message — condition met: 'if login fails'
- **Test ID:** TC_510B19
- **Type:** positive
- **Priority:** high
- **Precondition:** Ensure condition is met: if login fails
- **Steps:**
  1. Set up: if login fails
  1. Execute: show message & error message
- **Expected Result:** If login fails, display error message
 4.

### [Condition] Login shows message & error message — condition NOT met: 'if login fails'
- **Test ID:** TC_F70D6E
- **Type:** negative
- **Priority:** high
- **Precondition:** Ensure condition is NOT met: if login fails
- **Steps:**
  1. Set up without condition: if login fails
  1. Attempt to: show message & error message
- **Expected Result:** System blocks action or shows appropriate message

### [Security] Login shows message & error message — SQL injection attempt
- **Test ID:** TC_C9FD2B
- **Type:** security
- **Priority:** high
- **Precondition:** if login fails
- **Steps:**
  1. Navigate to the relevant input form
  1. Enter SQL injection payload: ' OR '1'='1
  1. Submit the form
- **Expected Result:** System sanitizes input, shows error or rejects request. No data exposed.

### [Security] Login shows message & error message — XSS attempt
- **Test ID:** TC_4EC961
- **Type:** security
- **Priority:** high
- **Precondition:** if login fails
- **Steps:**
  1. Navigate to the relevant input form
  1. Enter XSS payload: <script>alert('xss')</script>
  1. Submit the form
- **Expected Result:** System escapes or rejects malicious script. No script executes.


---

## Requirement: REQ_981DAD

### [Positive] Admin creates product & 5 with valid inputs
- **Test ID:** TC_F7E841
- **Type:** positive
- **Priority:** medium
- **Precondition:** Admin is logged in with admin privileges
- **Steps:**
  1. Navigate to create page / feature
  1. Enter valid product: 'valid input'
  1. Enter valid 5: 'valid input'
  1. Submit / Execute create
- **Expected Result:** can create new product listing
 5.

### [Negative] Admin creates product & 5 — invalid product
- **Test ID:** TC_6DE04F
- **Type:** negative
- **Priority:** medium
- **Precondition:** Admin is logged in with admin privileges
- **Steps:**
  1. Navigate to create page
  1. Enter invalid product: 'invalid input'
  1. Submit/proceed
- **Expected Result:** System shows error: invalid product

### [Negative] Admin creates product & 5 — invalid 5
- **Test ID:** TC_AA3554
- **Type:** negative
- **Priority:** medium
- **Precondition:** Admin is logged in with admin privileges
- **Steps:**
  1. Navigate to create page
  1. Enter invalid 5: 'invalid input'
  1. Submit/proceed
- **Expected Result:** System shows error: invalid 5

### [Edge] Admin creates product & 5 — empty product
- **Test ID:** TC_73D4CA
- **Type:** edge
- **Priority:** medium
- **Precondition:** Admin is logged in with admin privileges
- **Steps:**
  1. Navigate to create page
  1. Leave product empty
  1. Submit/proceed
- **Expected Result:** System shows required field error for product

### [Edge] Admin creates product & 5 — boundary product
- **Test ID:** TC_5A7503
- **Type:** edge
- **Priority:** low
- **Precondition:** Admin is logged in with admin privileges
- **Steps:**
  1. Navigate to create page
  1. Enter boundary value for product: 'boundary value'
  1. Submit/proceed
- **Expected Result:** System handles boundary value correctly

### [Edge] Admin creates product & 5 — empty 5
- **Test ID:** TC_A7D489
- **Type:** edge
- **Priority:** medium
- **Precondition:** Admin is logged in with admin privileges
- **Steps:**
  1. Navigate to create page
  1. Leave 5 empty
  1. Submit/proceed
- **Expected Result:** System shows required field error for 5

### [Edge] Admin creates product & 5 — boundary 5
- **Test ID:** TC_A39B29
- **Type:** edge
- **Priority:** low
- **Precondition:** Admin is logged in with admin privileges
- **Steps:**
  1. Navigate to create page
  1. Enter boundary value for 5: 'boundary value'
  1. Submit/proceed
- **Expected Result:** System handles boundary value correctly


---

## Requirement: REQ_263AE2

### [Positive] System checks inventory & 6 with valid inputs
- **Test ID:** TC_AE14E6
- **Type:** positive
- **Priority:** medium
- **Precondition:** System is running and accessible
- **Steps:**
  1. Navigate to check page / feature
  1. Enter valid inventory: 'valid input'
  1. Enter valid 6: 'valid input'
  1. Enter valid order: 'valid input'
  1. Submit / Execute check
- **Expected Result:** must check inventory before confirming order
 6.

### [Negative] System checks inventory & 6 — invalid inventory
- **Test ID:** TC_630A6D
- **Type:** negative
- **Priority:** medium
- **Precondition:** System is running and accessible
- **Steps:**
  1. Navigate to check page
  1. Enter invalid inventory: 'invalid input'
  1. Submit/proceed
- **Expected Result:** System shows error: invalid inventory

### [Negative] System checks inventory & 6 — invalid 6
- **Test ID:** TC_C76C44
- **Type:** negative
- **Priority:** medium
- **Precondition:** System is running and accessible
- **Steps:**
  1. Navigate to check page
  1. Enter invalid 6: 'invalid input'
  1. Submit/proceed
- **Expected Result:** System shows error: invalid 6

### [Negative] System checks inventory & 6 — invalid order
- **Test ID:** TC_0A267D
- **Type:** negative
- **Priority:** medium
- **Precondition:** System is running and accessible
- **Steps:**
  1. Navigate to check page
  1. Enter invalid order: 'invalid input'
  1. Submit/proceed
- **Expected Result:** System shows error: invalid order

### [Edge] System checks inventory & 6 — empty inventory
- **Test ID:** TC_ECAB0B
- **Type:** edge
- **Priority:** medium
- **Precondition:** System is running and accessible
- **Steps:**
  1. Navigate to check page
  1. Leave inventory empty
  1. Submit/proceed
- **Expected Result:** System shows required field error for inventory

### [Edge] System checks inventory & 6 — boundary inventory
- **Test ID:** TC_92E864
- **Type:** edge
- **Priority:** low
- **Precondition:** System is running and accessible
- **Steps:**
  1. Navigate to check page
  1. Enter boundary value for inventory: 'boundary value'
  1. Submit/proceed
- **Expected Result:** System handles boundary value correctly

### [Edge] System checks inventory & 6 — empty 6
- **Test ID:** TC_7FA66F
- **Type:** edge
- **Priority:** medium
- **Precondition:** System is running and accessible
- **Steps:**
  1. Navigate to check page
  1. Leave 6 empty
  1. Submit/proceed
- **Expected Result:** System shows required field error for 6

### [Edge] System checks inventory & 6 — boundary 6
- **Test ID:** TC_F12609
- **Type:** edge
- **Priority:** low
- **Precondition:** System is running and accessible
- **Steps:**
  1. Navigate to check page
  1. Enter boundary value for 6: 'boundary value'
  1. Submit/proceed
- **Expected Result:** System handles boundary value correctly


---

## Requirement: REQ_996EE8

### [Positive] Checkout submits 7 & confirmation email with valid inputs
- **Test ID:** TC_773336
- **Type:** positive
- **Priority:** medium
- **Precondition:** when checkout is complete
- **Steps:**
  1. Navigate to submit page / feature
  1. Enter valid form fields: 'valid input'
  1. Submit / Execute submit
- **Expected Result:** When checkout is complete, send confirmation email
 7.

### [Negative] Checkout submits 7 & confirmation email — invalid form fields
- **Test ID:** TC_6DF7EB
- **Type:** negative
- **Priority:** medium
- **Precondition:** when checkout is complete
- **Steps:**
  1. Navigate to submit page
  1. Enter invalid form fields: 'invalid input'
  1. Submit/proceed
- **Expected Result:** System shows error: invalid form fields

### [Edge] Checkout submits 7 & confirmation email — empty form fields
- **Test ID:** TC_D147E8
- **Type:** edge
- **Priority:** medium
- **Precondition:** when checkout is complete
- **Steps:**
  1. Navigate to submit page
  1. Leave form fields empty
  1. Submit/proceed
- **Expected Result:** System shows required field error for form fields

### [Edge] Checkout submits 7 & confirmation email — boundary form fields
- **Test ID:** TC_5587F2
- **Type:** edge
- **Priority:** low
- **Precondition:** when checkout is complete
- **Steps:**
  1. Navigate to submit page
  1. Enter boundary value for form fields: 'boundary value'
  1. Submit/proceed
- **Expected Result:** System handles boundary value correctly

### [Condition] Checkout submits 7 & confirmation email — condition met: 'when checkout is complete'
- **Test ID:** TC_1A193A
- **Type:** positive
- **Priority:** high
- **Precondition:** Ensure condition is met: when checkout is complete
- **Steps:**
  1. Set up: when checkout is complete
  1. Execute: submit 7 & confirmation email
- **Expected Result:** When checkout is complete, send confirmation email
 7.

### [Condition] Checkout submits 7 & confirmation email — condition NOT met: 'when checkout is complete'
- **Test ID:** TC_D63D74
- **Type:** negative
- **Priority:** high
- **Precondition:** Ensure condition is NOT met: when checkout is complete
- **Steps:**
  1. Set up without condition: when checkout is complete
  1. Attempt to: submit 7 & confirmation email
- **Expected Result:** System blocks action or shows appropriate message


---

## Requirement: REQ_F710BA

### [Positive] Password encrypts with valid inputs
- **Test ID:** TC_699A9C
- **Type:** positive
- **Priority:** high
- **Precondition:** Password has access to the system
- **Steps:**
  1. Navigate to encrypt page / feature
  1. Submit / Execute encrypt
- **Expected Result:** must be encrypted before storing

### [Negative] Password encrypts with invalid data
- **Test ID:** TC_67A437
- **Type:** negative
- **Priority:** medium
- **Precondition:** Password has access to the system
- **Steps:**
  1. Attempt to encrypt  with invalid/unauthorized data
- **Expected Result:** System shows appropriate error message

### [Security] Password encrypts — SQL injection attempt
- **Test ID:** TC_004AC0
- **Type:** security
- **Priority:** high
- **Precondition:** Password has access to the system
- **Steps:**
  1. Navigate to the relevant input form
  1. Enter SQL injection payload: ' OR '1'='1
  1. Submit the form
- **Expected Result:** System sanitizes input, shows error or rejects request. No data exposed.

### [Security] Password encrypts — XSS attempt
- **Test ID:** TC_D9BC67
- **Type:** security
- **Priority:** high
- **Precondition:** Password has access to the system
- **Steps:**
  1. Navigate to the relevant input form
  1. Enter XSS payload: <script>alert('xss')</script>
  1. Submit the form
- **Expected Result:** System escapes or rejects malicious script. No script executes.


---

