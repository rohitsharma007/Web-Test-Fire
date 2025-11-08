# Action Validation Prompt
# Validate Actions Before Execution for Safety and Effectiveness

## Task
Before executing ANY action during web exploration, validate that it is safe, appropriate, and valuable for testing.

## Input Data
You will receive:
1. **Proposed Action**: What the system wants to do
   - Action type (click, input, select, navigate)
   - Target element (text, selector, type)
   - Context (current URL, page state)

2. **Current State**:
   - Current URL
   - Page title
   - Previously taken actions
   - Step count and max steps

## Your Task
Determine if the proposed action should be:
- ✅ **APPROVED**: Safe and valuable, proceed
- ⚠️ **MODIFIED**: Needs adjustment before proceeding
- ❌ **REJECTED**: Unsafe or inappropriate, skip

## Validation Process

### STEP 1: Safety Check (Critical - Must Pass All)

#### Check 1.1: No Destructive Keywords
```
REJECT if element text contains:
- "delete", "remove", "erase"
- "cancel order", "cancel subscription"
- "close account", "deactivate"
- "permanently remove"
- "uninstall", "factory reset"

Example:
Element: "Delete Account" → ❌ REJECT
Reason: Destructive action that could harm account
```

#### Check 1.2: No Logout/Session End
```
REJECT if element text contains:
- "logout", "log out"
- "sign out", "signout"
- "exit", "end session"

Example:
Element: "Sign Out" → ❌ REJECT
Reason: Would end testing session prematurely
```

#### Check 1.3: No Financial Transactions
```
REJECT if element text contains:
- "purchase", "buy now", "complete purchase"
- "checkout", "pay now", "place order"
- "subscribe" (with payment)
- "confirm payment"

Example:
Element: "Place Order" → ❌ REJECT
Reason: Would attempt real transaction
```

#### Check 1.4: Domain Boundary
```
REJECT if action leads to external domain
(unless explicitly allowed for specific scenarios)

Example:
Element: Link to "facebook.com" → ❌ REJECT
Reason: External domain, out of scope
```

#### Check 1.5: File Download Safety
```
REJECT if element triggers download of:
- Executable files (.exe, .dmg, .app)
- Archive files (.zip, .tar, .rar) - unless expected
- Unknown file types

APPROVE for safe document downloads:
- .pdf (but log it)
- .csv, .xlsx (if testing export features)

Example:
Element: "Download Installer.exe" → ❌ REJECT
Element: "Download Report.pdf" → ⚠️ APPROVE with caution
```

### STEP 2: Value Check (Should Provide Testing Value)

#### Check 2.1: Not Already Done
```
REJECT if:
- Exact same action on exact same element already performed
- Very similar action already performed (e.g., clicked 5 products already)

APPROVE if:
- First time interacting with this element
- Similar but different element (e.g., different product)

Example:
Already clicked "Product 1", "Product 2", "Product 3"
Now proposing "Product 4" → ⚠️ MODIFY (maybe skip, low value)
```

#### Check 2.2: Provides Coverage
```
APPROVE if:
- Explores new functionality
- Tests different user workflow
- Covers different page type

REJECT if:
- Redundant testing
- No new information gained

Example:
Action: Click 20th product in list → ❌ REJECT
Reason: Already tested product detail page, diminishing returns
```

#### Check 2.3: Appropriate for Page Context
```
APPROVE if action makes sense in context:
- On login page → Fill login form (APPROVE)
- On search page → Enter search query (APPROVE)
- On product page → View details, add to cart (APPROVE)

REJECT if action doesn't fit context:
- On checkout page → Submit payment (REJECT)
- On profile page → Delete profile (REJECT)
```

### STEP 3: Execution Feasibility Check

#### Check 3.1: Element Available
```
VERIFY:
- Element is visible on page
- Element is not disabled
- Element is clickable (not behind overlay)

If element not found → ⚠️ MODIFY (wait and retry) or ❌ REJECT
```

#### Check 3.2: Required Data Available
```
For INPUT actions:
VERIFY we have appropriate sample data

Email input → Need: test@example.com ✅
Password input → Need: Test123!@# ✅
Credit card input → ❌ REJECT (don't test payment)

For SELECT actions:
VERIFY we can choose a safe option
```

#### Check 3.3: Page State Ready
```
VERIFY:
- Page is fully loaded
- No loading spinners active
- No pending AJAX requests (if detectable)

If page not ready → ⚠️ MODIFY (wait for stable state)
```

### STEP 4: Context Awareness

#### Check 4.1: Workflow Continuity
```
APPROVE if action continues logical workflow:
- Login page → Fill form → Submit → Good flow ✅
- Product page → Add to cart → View cart → Good flow ✅
- Cart page → Checkout → STOP before payment ⚠️

REJECT if action breaks workflow unnecessarily
```

#### Check 4.2: Testing Goals
```
APPROVE if action serves testing goals:
- Discover new pages ✅
- Test form validation ✅
- Verify navigation ✅
- Check UI responses ✅

REJECT if no clear testing benefit
```

## Output Format

Provide validation result in this format:

```json
{
  "validation_result": "APPROVED|MODIFIED|REJECTED",
  "safety_score": 10,
  "value_score": 8,
  "overall_score": 9,
  "reasoning": "Detailed explanation of decision",
  "concerns": ["List any concerns even if approved"],
  "modifications": ["If MODIFIED, list required changes"],
  "alternative_action": "If REJECTED, suggest alternative"
}
```

## Scoring System

### Safety Score (0-10)
- 10: Completely safe, no concerns
- 7-9: Safe with minor concerns
- 4-6: Moderate risk, needs modification
- 0-3: Unsafe, must reject

### Value Score (0-10)
- 10: High testing value, new coverage
- 7-9: Good value, useful testing
- 4-6: Moderate value, some usefulness
- 0-3: Low value, redundant or minimal benefit

### Overall Score
- Average of Safety and Value scores
- Minimum threshold: 5.0 to approve
- Below 5.0: Modify or reject

## Decision Matrix

| Safety Score | Value Score | Decision |
|--------------|-------------|----------|
| 8-10 | 8-10 | ✅ APPROVE |
| 8-10 | 5-7 | ✅ APPROVE |
| 8-10 | 0-4 | ⚠️ MODIFY or Skip |
| 5-7 | 8-10 | ⚠️ MODIFY (add safety measures) |
| 5-7 | 5-7 | ⚠️ MODIFY |
| 5-7 | 0-4 | ❌ REJECT |
| 0-4 | Any | ❌ REJECT |

## Examples

### Example 1: APPROVED

**Proposed Action:**
```
Action: Click
Element: "Login" button
URL: https://example.com
Context: Homepage, step 3 of 50
```

**Validation:**
```json
{
  "validation_result": "APPROVED",
  "safety_score": 10,
  "value_score": 10,
  "overall_score": 10,
  "reasoning": "Clicking 'Login' is completely safe (no destructive action), provides high testing value (authentication flow is critical user journey), and is contextually appropriate for homepage exploration. Element is visible and clickable.",
  "concerns": [],
  "modifications": [],
  "alternative_action": null
}
```

### Example 2: REJECTED

**Proposed Action:**
```
Action: Click
Element: "Delete Account" button
URL: https://example.com/settings
Context: Settings page, step 15 of 50
```

**Validation:**
```json
{
  "validation_result": "REJECTED",
  "safety_score": 0,
  "value_score": 3,
  "overall_score": 1.5,
  "reasoning": "This action contains the destructive keyword 'Delete Account' which would permanently remove the test account. Even though it might provide some testing value to see the confirmation flow, the risk is too high and violates our primary safety guardrail of no destructive actions.",
  "concerns": [
    "Destructive action keyword detected",
    "Could permanently delete account",
    "No way to recover if executed"
  ],
  "modifications": [],
  "alternative_action": "Click on 'Edit Profile' or 'Privacy Settings' instead to explore account management features safely"
}
```

### Example 3: MODIFIED

**Proposed Action:**
```
Action: Input
Element: Credit card field
Text to enter: "4111111111111111"
URL: https://example.com/checkout
Context: Checkout page, step 28 of 50
```

**Validation:**
```json
{
  "validation_result": "REJECTED",
  "safety_score": 2,
  "value_score": 5,
  "overall_score": 3.5,
  "reasoning": "While testing checkout flow has value, entering credit card information crosses into financial transaction territory which is explicitly prohibited. We should stop exploration before payment details entry.",
  "concerns": [
    "Checkout/payment page detected",
    "Credit card field should not be filled",
    "Risk of accidental purchase"
  ],
  "modifications": [
    "Stop before payment information",
    "Log that checkout page was reached",
    "Navigate back to safe area"
  ],
  "alternative_action": "Navigate back to cart or product pages. Log 'Reached checkout page - stopped before payment entry' as testing boundary."
}
```

### Example 4: MODIFIED (Wait for Page)

**Proposed Action:**
```
Action: Click
Element: "Submit" button
URL: https://example.com/form
Context: Form page, page still loading
```

**Validation:**
```json
{
  "validation_result": "MODIFIED",
  "safety_score": 9,
  "value_score": 8,
  "overall_score": 8.5,
  "reasoning": "The action itself is safe and valuable, but the page is still loading. We should wait for the page to fully stabilize before clicking submit to avoid race conditions or errors.",
  "concerns": [
    "Page not fully loaded",
    "Submit might fail or cause errors"
  ],
  "modifications": [
    "Wait 2-3 seconds for page to load completely",
    "Verify all form fields are visible and ready",
    "Then proceed with click"
  ],
  "alternative_action": null
}
```

### Example 5: APPROVED with Caution

**Proposed Action:**
```
Action: Click
Element: "Add to Cart" button
URL: https://example.com/product/123
Context: Product detail page, step 10 of 50
```

**Validation:**
```json
{
  "validation_result": "APPROVED",
  "safety_score": 9,
  "value_score": 9,
  "overall_score": 9,
  "reasoning": "Adding to cart is safe as it doesn't complete a purchase. It's valuable for testing e-commerce flow. However, we must ensure we stop before actual checkout/payment.",
  "concerns": [
    "Ensure we don't proceed to payment",
    "Watch for aggressive checkout prompts"
  ],
  "modifications": [],
  "alternative_action": null
}
```

## Quick Validation Checklist

Use this for rapid validation:

```
□ No destructive keywords (delete, remove, cancel order)?
□ No logout/sign out?
□ No purchase/payment/checkout?
□ No external domain navigation?
□ No dangerous file downloads?
□ Element is visible and clickable?
□ Action hasn't been repeated excessively?
□ Action provides testing value?
□ Page is in stable state?
□ We have required data (for inputs)?

If all ✅ → APPROVE
If any ❌ on safety items → REJECT
If ❌ on execution items → MODIFY
```

## Special Case Validations

### Validation for Repeated Actions
```
If proposing to click 3rd+ similar element:
- Evaluate diminishing returns
- If testing value low → REJECT
- Suggest moving to different functionality
```

### Validation for Multi-Step Forms
```
If on step 3 of 5 in a form:
- APPROVE continuing through steps
- But watch for payment/submission
- Validate each step's safety
```

### Validation for Search/Filter Actions
```
If proposing search or filter:
- APPROVE (useful testing)
- Verify search term is harmless
- Check results don't lead to violations
```

### Validation for Back/Navigation
```
If proposing to go back or navigate:
- Generally APPROVE
- Verify not navigating to unsafe area
- Check for workflow continuity
```

---

Use this validation prompt to ensure every action is safe, valuable, and appropriate before execution.
