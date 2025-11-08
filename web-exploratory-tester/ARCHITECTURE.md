# Architecture Documentation

## System Overview

The Web Exploratory Testing Framework uses a **multi-agent architecture** where specialized agents handle different aspects of the testing workflow. This design promotes modularity, maintainability, and extensibility.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                           main.py                                │
│                    (Orchestrator & Entry Point)                  │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                ┌───────────┴───────────┐
                │                       │
                ▼                       ▼
    ┌──────────────────┐    ┌──────────────────┐
    │  Core Modules    │    │     Agents       │
    └──────────────────┘    └──────────────────┘
                │                       │
        ┌───────┴───────┐       ┌──────┴──────────┐
        │               │       │                  │
        ▼               ▼       ▼                  ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────────┐
│   Browser    │  │    State     │  │    Explorer      │
│   Manager    │  │   Tracker    │  │     Agent        │
└──────────────┘  └──────────────┘  └──────────────────┘
        │               │                    │
        ▼               ▼                    ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────────┐
│    Action    │  │    Popup     │  │   Screenshot     │
│   Handler    │  │   Handler    │  │     Agent        │
└──────────────┘  └──────────────┘  └──────────────────┘
                                            │
                                            ▼
                                    ┌──────────────────┐
                                    │     Report       │
                                    │      Agent       │
                                    └──────────────────┘
```

## Core Components

### 1. Main Orchestrator (`main.py`)

**Purpose**: Entry point and workflow coordinator

**Responsibilities**:
- Parse command-line arguments
- Initialize all components
- Orchestrate the testing workflow
- Handle cleanup and error recovery

**Key Methods**:
- `run()`: Main execution flow
- `_initialize_components()`: Set up all agents and managers
- `_cleanup()`: Resource cleanup

**Data Flow**:
```
User Input → Argument Parser → Component Initialization → Exploration → Report Generation → Cleanup
```

### 2. Browser Manager (`core/browser_manager.py`)

**Purpose**: Manage browser lifecycle and provide interaction primitives

**Responsibilities**:
- Launch and configure Playwright browser
- Handle page navigation
- Execute low-level interactions (click, type, scroll)
- Capture screenshots
- Manage browser context and sessions

**Key APIs**:
```python
await browser.start()
await browser.navigate(url)
await browser.click_element(selector)
await browser.type_text(selector, text)
await browser.get_visible_elements()
await browser.take_screenshot(path)
await browser.close()
```

**Technology**: Playwright (Chromium)

### 3. State Tracker (`core/state_tracker.py`)

**Purpose**: Maintain session memory and prevent loops

**Responsibilities**:
- Track visited URLs
- Record all interactions
- Prevent duplicate actions
- Maintain session statistics
- Export session data

**Data Structures**:
- `visited_urls: Set[str]` - Normalized URLs visited
- `visited_url_patterns: Set[str]` - URL patterns to detect similar pages
- `interacted_elements: Set[str]` - Element identifiers
- `interaction_history: List[InteractionRecord]` - Complete history

**Key Methods**:
```python
tracker.has_visited_url(url) → bool
tracker.mark_url_visited(url)
tracker.record_interaction(...) → InteractionRecord
tracker.get_summary() → Dict
tracker.export_to_json(filepath)
```

### 4. Action Handler (`core/action_handler.py`)

**Purpose**: Execute and validate UI interactions

**Responsibilities**:
- Execute clicks, inputs, selections
- Provide sample data for forms
- Validate action safety
- Verify action results

**Action Types**:
- **Click**: Button, link, element clicks
- **Input**: Text, email, password entry
- **Select**: Dropdown selections
- **Scroll**: Page scrolling

**Safety Checks**:
```python
is_safe_action(element_text) → bool
```

Prevents destructive actions like:
- Delete, Remove
- Logout, Sign Out
- Purchase, Checkout
- Unsubscribe, Deactivate

### 5. Popup Handler (`core/popup_handler.py`)

**Purpose**: Automatically handle popups and modals

**Responsibilities**:
- Detect and dismiss JavaScript dialogs
- Handle cookie consent banners
- Close modals and overlays
- Accept/dismiss based on content

**Detection Strategies**:
- Dialog events: `page.on("dialog")`
- CSS selectors: `[role="dialog"]`, `.modal`, `.cookie-banner`
- Text matching: "accept", "close", "dismiss"

**Action Logic**:
```python
if text.contains("accept cookies") → Click Accept
if text.contains("delete") → Dismiss
if modal with close button → Click Close
```

## Agent Architecture

### 1. Explorer Agent (`agents/explorer_agent.py`)

**Role**: Core AI decision-making brain

**Responsibilities**:
- Navigate starting URL
- Scan page for interactive elements
- Apply AI reasoning to select actions
- Execute actions via ActionHandler
- Coordinate screenshot capture
- Record interactions in StateTracker
- Determine when exploration is complete

**Exploration Algorithm**:
```python
while steps < max_steps:
    elements = get_visible_elements()

    # Filter candidates
    candidates = filter_safe_unexplored_elements(elements)

    # Prioritize using AI reasoning
    for element in candidates:
        element.priority = calculate_priority(element)

    # Select best action
    action = select_top_priority_action(candidates)

    # Execute
    result = execute_action(action)

    # Capture evidence
    screenshot = capture_screenshot()

    # Record
    record_interaction(result, screenshot)
```

**Priority Calculation**:
```python
Priority = Base Score (by tag)
         + Keyword Score (high/medium/low)
         + Text Clarity Score
         + Navigation Potential Score
         + Randomness (for variety)
```

**Keywords**:
- High Priority: login, search, submit, next, continue
- Medium Priority: register, learn more, view, explore
- Low Priority: about, contact, help, faq

### 2. Screenshot Agent (`agents/screenshot_agent.py`)

**Role**: Visual documentation manager

**Responsibilities**:
- Capture screenshots after each action
- Generate meaningful filenames
- Maintain screenshot metadata
- Export metadata index
- Manage storage

**Filename Format**:
```
step_{number:03d}_{action_description}.png
Example: step_005_click_login.png
```

**Metadata Structure**:
```json
{
  "step_number": 5,
  "filename": "step_005_click_login.png",
  "filepath": "/path/to/screenshot.png",
  "timestamp": "2025-11-08T14:23:45",
  "action_description": "click_login",
  "url": "https://example.com/login",
  "page_title": "Login Page",
  "file_size_kb": 245
}
```

### 3. Report Agent (`agents/report_agent.py`)

**Role**: PDF report compilation

**Responsibilities**:
- Generate comprehensive PDF reports
- Embed screenshots
- Format exploration data
- Provide insights and recommendations

**Report Structure**:

1. **Cover Page**
   - Title
   - Target URL
   - Timestamp
   - Framework info

2. **Summary Page**
   - General information
   - Statistics (steps, URLs, actions)
   - Configuration settings

3. **Step Documentation** (for each interaction)
   - Step number and type
   - Action description
   - Element details
   - URL and timestamp
   - Success/failure status
   - Screenshot (embedded)

4. **Observations Page**
   - Failed interactions
   - Automated actions (popups)
   - Coverage summary
   - Recommendations

**Technology**: FPDF2 library

## Data Flow

### Exploration Flow

```
1. User provides URL
        ↓
2. Main initializes components
        ↓
3. Browser navigates to URL
        ↓
4. Explorer scans page
        ↓
5. AI selects next action
        ↓
6. ActionHandler executes
        ↓
7. PopupHandler manages dialogs
        ↓
8. ScreenshotAgent captures
        ↓
9. StateTracker records
        ↓
10. Repeat 4-9 until complete
        ↓
11. ReportAgent generates PDF
        ↓
12. Output delivered to user
```

### Data Persistence

**During Exploration**:
- In-memory tracking via StateTracker
- Real-time screenshot saving
- Console logging

**After Exploration**:
- `logs/session_data.json` - Complete interaction history
- `logs/screenshot_metadata.json` - Screenshot index
- `logs/exploration.log` - Execution log
- `outputs/screenshots/*.png` - Screenshot files
- `outputs/reports/*.pdf` - Final PDF report

## Decision Making Logic

### Element Selection Algorithm

```python
def select_next_action(elements):
    # Step 1: Filter
    candidates = []
    for element in elements:
        if already_interacted(element):
            continue
        if is_unsafe(element):
            continue
        if should_skip(element):
            continue
        candidates.append(element)

    # Step 2: Prioritize
    for element in candidates:
        score = 0

        # Tag-based scoring
        if element.tag == 'button':
            score += 10
        elif element.tag == 'a':
            score += 8
        elif element.tag == 'input':
            score += 7

        # Keyword-based scoring
        for keyword in HIGH_PRIORITY_KEYWORDS:
            if keyword in element.text.lower():
                score += 15

        element.priority = score

    # Step 3: Select
    candidates.sort(key=lambda x: x.priority, reverse=True)

    # 70% pick highest, 30% variety
    if random() < 0.7:
        return candidates[0]
    else:
        return choice(candidates[:3])
```

### Form Input Strategy

```python
def get_sample_data(field_text, field_type):
    if 'email' in field_text.lower():
        return 'test@example.com'
    elif 'name' in field_text.lower():
        return 'John Doe'
    elif 'password' in field_text.lower():
        return 'Test123!'
    elif 'search' in field_text.lower():
        return 'test'
    else:
        return 'Test input'
```

## Extension Points

### Adding New Actions

1. Add action type to `ActionHandler`:
```python
async def execute_hover(self, selector, text):
    # Implementation
    pass
```

2. Update `ExplorerAgent` to recognize and use:
```python
def _create_action(self, element):
    if element.needs_hover:
        return {'type': 'hover', ...}
```

### Custom AI Integration

Replace priority calculation with LLM calls:

```python
# In ExplorerAgent
async def _select_next_action(self, elements):
    # Send elements to LLM
    response = await llm.analyze(elements, context=self.state_tracker)

    # Parse LLM response
    selected_element = parse_llm_choice(response)

    return self._create_action(selected_element)
```

### Adding Vision Analysis

```python
# In ScreenshotAgent
async def analyze_screenshot(self, image_path):
    # Send to vision model
    analysis = await vision_model.analyze(image_path)

    # Detect anomalies
    if analysis.has_visual_bugs:
        self.logger.warning(f"Visual issue: {analysis.description}")
```

## Performance Optimization

### Memory Management
- Limit screenshot retention
- Stream large reports
- Clear browser cache periodically

### Speed Optimization
- Parallel element analysis
- Cached URL normalization
- Efficient selector strategies

### Scalability
- Configurable delays between actions
- Rate limiting
- Resource pooling for multiple tests

## Error Handling Strategy

### Levels

1. **Element-level**: Retry with different selector
2. **Action-level**: Skip and continue
3. **Page-level**: Navigate back or refresh
4. **Session-level**: Log and continue with next step
5. **Critical**: Cleanup and exit gracefully

### Recovery Mechanisms

```python
try:
    await action()
except ElementNotFound:
    log_error()
    consecutive_failures += 1
    if consecutive_failures > 5:
        break
except BrowserCrashed:
    await restart_browser()
    await navigate_to_last_url()
```

## Security Considerations

### Safe Exploration
- No credential brute-forcing
- Respect robots.txt (manual check)
- Same-domain restriction
- Avoid destructive actions

### Data Privacy
- No sensitive data storage
- Local-only processing
- Configurable output retention

## Future Architecture Enhancements

1. **Plugin System**: Load custom agents dynamically
2. **Distributed Mode**: Multi-browser parallel exploration
3. **Real-time Dashboard**: Live exploration monitoring
4. **Event Streaming**: Publish events to external systems
5. **ML Training**: Learn from successful explorations

---

**Version**: 1.0.0
**Last Updated**: 2025-11-08
