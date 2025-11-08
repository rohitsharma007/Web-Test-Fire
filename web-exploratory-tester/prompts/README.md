# AI Prompts for Web Exploratory Testing

This directory contains comprehensive AI prompts that guide the exploratory testing framework through intelligent, safe, and effective web application testing.

## Overview

These prompts provide **step-by-step guardrails** to ensure robust, reliable testing results. They can be used:

1. **As Reference Documentation**: Read by developers to understand decision-making logic
2. **As LLM Integration**: Feed directly to AI models (GPT-4, Claude, etc.) for intelligent automation
3. **As Training Material**: Learn how to perform effective exploratory testing

## Prompt Files

### 📋 Master Exploration Prompt
**File**: `master_exploration_prompt.md` (400+ lines)

The complete playbook for web exploratory testing.

**Contents**:
- Your Role & Core Principles
- 7-Phase Step-by-Step Process
- Special Scenario Handling
- Guardrails Summary
- Error Recovery Strategies
- Example Exploration Flow

**Use When**: System initialization, overall guidance reference

**Key Sections**:
- Phase 1: Page Load and Observation
- Phase 2: Element Discovery and Prioritization
- Phase 3: Action Selection and Validation
- Phase 4: Action Execution
- Phase 5: Post-Action Validation
- Phase 6: Decision Loop
- Phase 7: Reporting and Summary

### 🎯 Element Selection Prompt
**File**: `element_selection_prompt.md` (200+ lines)

Intelligent element selection and prioritization logic.

**Purpose**: Choose the BEST next element to interact with

**Decision Process**:
1. Eliminate unsafe elements
2. Score remaining elements
3. Apply reasoning
4. Select best option

**Includes**:
- Scoring algorithm with weights
- Priority keyword lists
- Context awareness rules
- Confidence levels
- Example selections

**Use When**: Choosing next action from multiple available elements

### ✅ Action Validation Prompt
**File**: `action_validation_prompt.md` (300+ lines)

Comprehensive action validation before execution.

**Purpose**: Ensure every action is safe and valuable

**Validation Steps**:
1. Safety Check (Critical)
   - No destructive keywords
   - No logout/session end
   - No financial transactions
   - Domain boundary check
   - File download safety
2. Value Check
   - Not already done
   - Provides coverage
   - Appropriate for context
3. Execution Feasibility
   - Element available
   - Required data ready
   - Page state stable
4. Context Awareness
   - Workflow continuity
   - Testing goals

**Outputs**: APPROVED / MODIFIED / REJECTED with reasoning

**Use When**: Before executing EVERY action

### 💡 Insights Generation Prompt
**File**: `insights_generation_prompt.md` (250+ lines)

Generate meaningful insights from exploration data.

**Purpose**: Analyze results and provide actionable recommendations

**Analysis Phases**:
1. Functional Analysis (workflows, features)
2. Usability Analysis (UX observations)
3. Issue Identification (bugs, problems)
4. Coverage Analysis (what was tested)
5. Recommendations (next steps)

**Outputs**: Comprehensive markdown report with:
- Executive summary
- Metrics overview
- Observations and findings
- Potential issues (Critical/Medium/Low)
- Recommendations for dev/QA teams

**Use When**: After exploration completes, for final reporting

### ⚙️ Configuration File
**File**: `prompt_config.yaml`

Configuration settings for prompt usage.

**Contains**:
- Prompt file mappings
- Guardrails and safety rules
- Priority keywords and weights
- Decision thresholds
- Integration settings
- Scenario templates

**Use When**: Configuring system behavior

### 📖 Integration Guide
**File**: `INTEGRATION_GUIDE.md` (500+ lines)

Complete guide to integrate prompts with LLM APIs.

**Includes**:
- Step-by-step integration instructions
- Code examples for OpenAI, Anthropic, Ollama
- Usage examples
- Cost considerations
- Best practices
- Troubleshooting

**Use When**: Implementing LLM-powered exploration

## Quick Start

### Option 1: Use as Reference (Current Implementation)

The framework already implements the logic from these prompts in Python code. The prompts serve as documentation.

**No changes needed** - just read the prompts to understand the decision-making logic.

### Option 2: Enable LLM Integration (Advanced)

For true AI-powered decision making:

1. **Install LLM client**:
   ```bash
   pip install openai  # or anthropic, or ollama
   ```

2. **Set API key**:
   ```bash
   export OPENAI_API_KEY=your_key_here
   ```

3. **Run with LLM**:
   ```bash
   python main.py --url https://example.com --use-llm
   ```

See `INTEGRATION_GUIDE.md` for complete instructions.

## Guardrails Summary

### ✅ MUST DO (Enforced by Prompts)

- Verify action safety before execution
- Use only sample/test data in forms
- Handle popups and modals automatically
- Capture screenshot after every action
- Log all actions with context
- Stay within same domain
- Respect rate limits (1-2 second delays)
- Stop at max iterations

### ❌ MUST NOT DO (Prevented by Prompts)

- Delete or remove any data
- Logout or close accounts
- Make purchases or financial transactions
- Use real personal information
- Bypass security measures
- Navigate to external domains
- Download executable files
- Submit forms that could harm production
- Attempt to exploit vulnerabilities

## Prompt Usage Flow

```
┌─────────────────────────────────────┐
│  1. Load Master Prompt              │
│     (System initialization)         │
└────────────┬────────────────────────┘
             ▼
┌─────────────────────────────────────┐
│  2. Page Load & Observation         │
│     (Scan page, handle popups)      │
└────────────┬────────────────────────┘
             ▼
┌─────────────────────────────────────┐
│  3. Element Selection Prompt        │
│     (Choose best next action)       │
└────────────┬────────────────────────┘
             ▼
┌─────────────────────────────────────┐
│  4. Action Validation Prompt        │
│     (Verify safety and value)       │
└────────────┬────────────────────────┘
             ▼
       ┌──────────┐
       │ Approved?│
       └────┬─────┘
            │
      ┌─────┴─────┐
      │           │
     Yes         No
      │           │
      ▼           ▼
┌──────────┐  ┌────────┐
│ Execute  │  │ Skip & │
│ Action   │  │ Next   │
└────┬─────┘  └────────┘
     │
     ▼
┌─────────────────────────────────────┐
│  5. Capture Screenshot & Log        │
└────────────┬────────────────────────┘
             │
             ▼
       ┌────────────┐
       │ More steps?│
       └─────┬──────┘
             │
       ┌─────┴─────┐
       │           │
      Yes         No
       │           │
       │           ▼
       │  ┌──────────────────────────┐
       │  │ 6. Insights Generation   │
       │  │    Prompt (Final Report) │
       │  └──────────────────────────┘
       │
       └──► Return to Step 2
```

## Sample Data Provided

The prompts specify exact sample data to use:

- **Email**: `test@example.com`
- **Name**: `John Doe`, `Jane Smith`
- **Password**: `Test123!@#`
- **Search**: `test`, `demo`, `example`
- **Phone**: `555-0100`
- **Address**: `123 Test Street`

This ensures consistent, safe testing without real data.

## Priority Keywords

### High Priority (Score: 15-20)
- login, sign in, search
- get started, start, submit
- continue, next

### Medium Priority (Score: 8-14)
- register, sign up
- learn more, view details
- explore, browse, menu

### Low Priority (Score: 3-7)
- about, contact, help
- faq, terms, privacy

## Decision Thresholds

From `prompt_config.yaml`:

- **Minimum Safety Score**: 7.0/10 (must pass)
- **Minimum Value Score**: 5.0/10 (for approval)
- **Minimum Overall Score**: 5.0/10 (combined)
- **Max Consecutive Failures**: 5 (then stop)
- **Max Similar Actions**: 3 (don't repeat)

## Examples

### Example: Login Flow

**Prompt Guidance**:
```
Step 1: Identify login button (High Priority: +20)
Step 2: Click login → Navigate to form
Step 3: Fill email: test@example.com
Step 4: Fill password: Test123!@#
Step 5: Click submit
Step 6: Observe error (EXPECTED with fake credentials)
Step 7: Log result and continue
```

### Example: E-commerce Browse

**Prompt Guidance**:
```
Step 1: Click "Products" (High Priority: +15)
Step 2: Select category filter
Step 3: Click product (Medium Priority: +12)
Step 4: View product details
Step 5: Click "Add to Cart" (Safe: +9)
Step 6: View cart contents
Step 7: STOP before checkout (Guardrail)
```

### Example: Search Testing

**Prompt Guidance**:
```
Step 1: Find search box (High Priority: +18)
Step 2: Enter "test" (Sample data)
Step 3: Submit search
Step 4: Observe results
Step 5: Click first result (Medium: +10)
Step 6: Validate detail page loaded
```

## Customization

### Adding New Priority Keywords

Edit `prompt_config.yaml`:

```yaml
priority_keywords:
  high_priority:
    - "your_keyword"
    - "another_keyword"
    weight: 20
```

### Adding New Sample Data

Edit any prompt file's sample data section:

```markdown
### Custom Sample Data
- Industry-specific field: "Custom value"
- Special format: "Your format"
```

### Adjusting Thresholds

Edit `prompt_config.yaml`:

```yaml
thresholds:
  min_safety_score: 8.0  # More strict
  min_value_score: 6.0   # More strict
```

## Troubleshooting

### Issue: Actions Too Conservative

**Solution**: Lower safety thresholds in `prompt_config.yaml`

### Issue: Not Exploring Deeply

**Solution**: Increase value score for less common elements

### Issue: Repeating Same Actions

**Solution**: Check `max_similar_actions` threshold

### Issue: Skipping Important Elements

**Solution**: Add keywords to high_priority list

## Benefits of Prompt-Driven Testing

### 1. Consistency
- Same logic applied every time
- Predictable behavior
- Reproducible results

### 2. Safety
- Multiple guardrails at every step
- Comprehensive validation
- Risk mitigation

### 3. Transparency
- Clear reasoning for every decision
- Documented thought process
- Auditable logic

### 4. Adaptability
- Easy to modify behavior
- Add new scenarios
- Adjust priorities

### 5. Intelligence
- Context-aware decisions
- Workflow understanding
- Value-based selection

## Extending the Prompts

### Add New Scenario

Create new section in `master_exploration_prompt.md`:

```markdown
### Scenario X: Your New Scenario
WHEN: [Trigger condition]
DO:
1. [Step 1]
2. [Step 2]
3. [Step 3]

GUARDRAIL: [Safety rule]
```

### Add New Validation Rule

Add to `action_validation_prompt.md`:

```markdown
#### Check X.X: Your New Check
VERIFY:
- [Condition 1]
- [Condition 2]

If fails → REJECT
```

### Add Custom Insights

Extend `insights_generation_prompt.md`:

```markdown
### Phase X: Your Custom Analysis
Analyze for:
- [Metric 1]
- [Metric 2]
```

## Version History

- **v1.0** (2025-11-08): Initial prompt set
  - Master exploration prompt
  - Element selection prompt
  - Action validation prompt
  - Insights generation prompt
  - Configuration file
  - Integration guide

## Next Steps

1. **Read the prompts**: Understand the decision logic
2. **Run the framework**: See prompts in action (heuristic mode)
3. **Optional**: Enable LLM mode for true AI reasoning
4. **Customize**: Adjust for your specific needs
5. **Extend**: Add new scenarios and rules

## Support

For questions or issues with prompts:

1. Check `INTEGRATION_GUIDE.md` for LLM setup
2. Review `prompt_config.yaml` for settings
3. Read specific prompt files for details
4. Check main `README.md` for framework usage

---

**These prompts ensure robust, safe, and intelligent web exploratory testing!**
