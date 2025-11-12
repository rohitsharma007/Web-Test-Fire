# AI-Driven Web Exploratory Testing Framework

An intelligent, autonomous web testing framework that explores websites like a human QA tester - observing, reasoning, and acting to discover workflows, UI behaviors, and page transitions.

## Overview

This framework uses a multi-agent architecture to:
- **Autonomously navigate** websites with AI-powered decision making
- **Intelligently interact** with UI elements (clicks, forms, navigation)
- **Handle popups** and modals automatically
- **Capture screenshots** at every meaningful step
- **Generate comprehensive PDF reports** documenting the entire exploration

### Key Features

- **Intelligent Navigation**: AI reasoning to select and interact with elements
- **Automatic Login**: Detects and handles login forms with provided credentials
- **Safe Exploration**: Avoids destructive actions (delete, logout, purchase)
- **Automatic Popup Handling**: Manages cookie banners, dialogs, and modals
- **Screenshot Documentation**: Visual evidence for every action
- **PDF Report Generation**: Professional reports with step-by-step documentation
- **State Tracking**: Prevents loops and duplicate interactions
- **Customizable**: Configurable depth, steps, and exploration strategies

## Architecture

```
web-exploratory-tester/
├── main.py                    # Entry point
├── agents/                    # AI agents
│   ├── explorer_agent.py      # Core decision-making brain
│   ├── screenshot_agent.py    # Screenshot capture & metadata
│   └── report_agent.py        # PDF report generation
├── core/                      # Core functionality
│   ├── browser_manager.py     # Browser lifecycle management
│   ├── action_handler.py      # UI interaction execution
│   ├── state_tracker.py       # Session memory & tracking
│   ├── popup_handler.py       # Popup/modal handling
│   └── utils.py              # Utility functions
├── prompts/                   # 🆕 AI guidance prompts (1,500+ lines)
│   ├── master_exploration_prompt.md      # Complete step-by-step guidance
│   ├── element_selection_prompt.md       # Element selection logic
│   ├── action_validation_prompt.md       # Safety validation rules
│   ├── insights_generation_prompt.md     # Report insights generation
│   ├── prompt_config.yaml                # Configuration & guardrails
│   ├── INTEGRATION_GUIDE.md              # LLM integration guide
│   └── README.md                          # Prompts documentation
├── outputs/
│   ├── screenshots/           # Captured screenshots
│   └── reports/              # Generated PDF reports
├── logs/                      # Execution logs
└── requirements.txt           # Python dependencies
```

## Installation

### Prerequisites

- Python 3.11 or higher
- pip (Python package manager)

### Setup

1. **Clone or download the framework**:
   ```bash
   cd web-exploratory-tester
   ```

2. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Install Playwright browsers**:
   ```bash
   playwright install chromium
   ```

That's it! You're ready to run exploratory tests.

## Usage

### Basic Usage

Test any website with a single command:

```bash
python main.py --url https://example.com
```

### Advanced Options

```bash
python main.py --url https://example.com \
    --max-steps 100 \
    --depth 5 \
    --headless True
```

### Command-Line Arguments

| Argument | Description | Default |
|----------|-------------|---------|
| `--url` | Target URL to explore (required) | - |
| `--max-steps` | Maximum exploration steps | 50 |
| `--depth` | Maximum navigation depth | 3 |
| `--headless` | Run browser in headless mode | False (browser visible) |
| `--output` | Base directory for outputs | outputs |
| `--username` | Username for automatic login (optional) | - |
| `--password` | Password for automatic login (optional) | - |

### Examples

**Scenario 1: Testing with Automatic Login (OrangeHRM Demo)**
```bash
python3 main.py --url https://opensource-demo.orangehrmlive.com \
  --username Admin --password admin123 --max-steps 25
```

**Scenario 2: Your Custom Application with Authentication**
```bash
python3 main.py --url https://your-app.com/login \
  --username testuser --password testpass123
```

**Scenario 3: Public Site (No Login Required)**
```bash
python3 main.py --url https://example.com --max-steps 50
# Works normally, no login attempt
```

**Extended exploration (headless mode for faster execution):**
```bash
python main.py --url https://example.com --max-steps 100 --headless True
```

**Deep exploration:**
```bash
python main.py --url https://example.com --depth 5 --max-steps 200
```

## Output

After exploration, the framework generates:

### 1. Screenshots
- Location: `outputs/screenshots/`
- Format: `step_NNN_action_description.png`
- One screenshot per action

### 2. PDF Report
- Location: `outputs/reports/`
- Filename: `exploration_report_[domain]_[timestamp].pdf`
- Contains:
  - Cover page with target URL and date
  - Summary statistics
  - Step-by-step documentation with screenshots
  - Observations and recommendations

### 3. Session Data
- Location: `logs/session_data.json`
- Complete interaction history in JSON format

### 4. Execution Logs
- Location: `logs/exploration.log`
- Detailed execution log with timestamps

## Intelligent Automatic Login

The framework now includes **AI-driven automatic login detection and execution**. When you provide credentials, the system intelligently:

### How It Works

1. **Detects Login Pages** - Analyzes URL, page title, and form elements to identify login pages
2. **Finds Form Fields** - Intelligently locates username/email and password input fields
3. **Fills Credentials** - Automatically enters the provided username and password
4. **Submits Form** - Finds and clicks the login button (or presses Enter)
5. **Verifies Success** - Checks if login was successful before continuing exploration
6. **Continues Testing** - Explores authenticated areas of the application

### When to Use

Provide `--username` and `--password` when:
- Testing applications that require authentication
- Exploring features behind login walls
- Testing user-specific workflows
- Validating authenticated user experiences

### What It Detects

The system recognizes login pages by looking for:
- Password input fields (`input[type="password"]`)
- Username/email fields with common labels
- URLs containing: `login`, `signin`, `auth`
- Page titles mentioning login or sign in
- Submit buttons with login-related text

### Example Output

```
[INFO] Credentials provided - will attempt automatic login
[INFO] Login page detected - attempting automatic login
[INFO] Attempting login with username: Admin
[INFO] Found login form fields - filling credentials...
[INFO] Username entered successfully
[INFO] Password entered successfully
[INFO] Clicking submit button: Login
[INFO] Login successful! Now at: https://app.com/dashboard
[INFO] Login successful! Continuing exploration...
```

## How It Works

### 1. Initialization
- Starts Playwright browser
- Sets up agents (Explorer, Screenshot, Report)
- Initializes state tracker

### 2. Exploration Loop
The Explorer Agent:
1. Loads the target URL
2. Scans for visible interactive elements
3. Uses AI reasoning to select the best action:
   - Prioritizes navigation elements
   - Fills forms with sample data
   - Avoids destructive actions
   - Skips already-visited elements
4. Executes the action
5. Captures screenshot
6. Records the interaction
7. Repeats until max steps or no more actions

### 3. Intelligent Decision Making

The framework reasons like a human QA tester:

**High Priority Actions:**
- Login, Sign In
- Get Started, Continue, Next
- Search, Submit
- Main navigation elements

**Medium Priority:**
- Register, Sign Up
- Learn More, View Details
- Explore, Browse

**Skipped Actions:**
- Logout, Delete, Remove
- Purchase, Checkout, Pay
- Destructive operations

### 4. Form Handling

Automatically fills forms with realistic data:
- Email fields: `test@example.com`
- Name fields: `John Doe`, `Jane Smith`
- Search fields: `test`, `search`, `demo`
- Password fields: `Test123!`

### 5. Popup Management

Automatically handles:
- Cookie consent banners → Click "Accept"
- JavaScript alerts → Accept safe dialogs
- Modals and overlays → Close if safe
- Permission requests → Handle appropriately

### 6. Report Generation

Creates a professional PDF with:
- Executive summary
- Exploration statistics
- Step-by-step screenshots
- Failed interactions
- Observations and recommendations

## AI Reasoning Rules

The Explorer Agent follows these principles:

1. **Safety First**: Never perform destructive actions
2. **Intelligent Navigation**: Prioritize elements that lead to new content
3. **Form Intelligence**: Fill inputs with appropriate sample data
4. **Loop Prevention**: Track and avoid duplicate interactions
5. **Context Awareness**: Understand element purpose from text and attributes
6. **Error Handling**: Gracefully handle failures and continue exploration

## 🆕 AI Prompt System with Step-by-Step Guardrails

The framework includes a comprehensive AI prompt system (1,500+ lines) that provides detailed step-by-step guidance for robust, safe testing. These prompts can be used as:
- **Documentation**: Understand the decision-making logic
- **LLM Integration**: Power true AI-driven exploration with GPT-4, Claude, etc.
- **Training Material**: Learn effective exploratory testing techniques

### Prompt Files

**📋 Master Exploration Prompt** (`prompts/master_exploration_prompt.md`)
- Complete 7-phase step-by-step process
- Guardrails for every decision point
- Special scenario handling (login, forms, e-commerce)
- Error recovery strategies
- 400+ lines of comprehensive guidance

**🎯 Element Selection Prompt** (`prompts/element_selection_prompt.md`)
- Intelligent element prioritization
- Scoring algorithm with weights
- Context-aware decision making
- Examples for different page types

**✅ Action Validation Prompt** (`prompts/action_validation_prompt.md`)
- Multi-level safety validation
- Value assessment framework
- APPROVED/MODIFIED/REJECTED workflow
- Quick validation checklist

**💡 Insights Generation Prompt** (`prompts/insights_generation_prompt.md`)
- Comprehensive analysis framework
- Issue categorization (Critical/Medium/Low)
- Actionable recommendations
- Structured report generation

**⚙️ Configuration** (`prompts/prompt_config.yaml`)
- Guardrails and safety rules
- Priority keywords and weights
- Decision thresholds
- Sample data specifications

**📖 Integration Guide** (`prompts/INTEGRATION_GUIDE.md`)
- Step-by-step LLM integration
- Code examples for OpenAI, Anthropic, Ollama
- Cost analysis and best practices
- Complete implementation guide

### Using the Prompt System

**Option 1: Reference Mode (Default)**
The framework already implements the prompt logic in code. No changes needed!

**Option 2: LLM-Powered Mode (Advanced)**
Enable true AI decision-making with language models:

```bash
# Install LLM client
pip install openai  # or anthropic

# Set API key
export OPENAI_API_KEY=your_key_here

# Run with LLM
python main.py --url https://example.com --use-llm
```

See `prompts/INTEGRATION_GUIDE.md` for complete instructions.

### Guardrails Enforced

**Safety Rules:**
- ✅ No destructive actions (delete, remove)
- ✅ No logout or session termination
- ✅ No financial transactions (purchase, checkout)
- ✅ Stay within same domain
- ✅ Use only sample test data

**Decision Thresholds:**
- Minimum safety score: 7.0/10
- Minimum value score: 5.0/10
- Max consecutive failures: 5
- Max similar actions: 3

For complete details, see `prompts/README.md`.

## Customization

### Extending the Framework

**Add custom sample data:**
Edit `core/action_handler.py` and modify:
```python
SAMPLE_EMAILS = ['custom@email.com']
SAMPLE_NAMES = ['Custom Name']
```

**Adjust element priorities:**
Edit `agents/explorer_agent.py` and modify:
```python
PRIORITY_KEYWORDS = {
    'high': ['your', 'keywords'],
    # ...
}
```

**Change screenshot settings:**
In `main.py`:
```python
self.screenshot_agent = ScreenshotAgent(
    full_page=True,  # Capture full page
    # ...
)
```

## Troubleshooting

### Common Issues

**Issue: "playwright not found"**
```bash
pip install playwright
playwright install chromium
```

**Issue: Browser fails to start**
- Check if running in environment without display (servers, Docker, etc.)
- If no display available, use `--headless True` flag
- On systems with display, browser will open visibly by default

**Issue: No elements found**
- Website might use JavaScript frameworks that load slowly
- Try increasing wait times in `browser_manager.py`

**Issue: PDF generation fails**
```bash
pip install --upgrade fpdf2
```

### Debug Mode

Enable verbose logging by editing `main.py`:
```python
self.logger = setup_logger("WebExploratoryTester", log_file, level=logging.DEBUG)
```

## Performance Considerations

- **Headless mode**: Faster execution, lower resource usage
- **Screenshot optimization**: Viewport-only screenshots reduce file size
- **Rate limiting**: Built-in delays prevent overwhelming servers
- **Memory management**: Old screenshots auto-cleanup available

## Security & Ethics

### Important Guidelines

✅ **Do:**
- Test authorized websites only
- Respect `robots.txt`
- Use for QA, testing, and security research
- Test on development/staging environments

❌ **Don't:**
- Test unauthorized websites
- Perform credential brute-forcing
- Create denial-of-service conditions
- Exploit discovered vulnerabilities without permission

This tool is for **authorized testing only**. Always obtain proper permission before testing any website.

## Limitations

- **JavaScript-heavy sites**: May have timing issues with dynamic content
- **Complex authentication**: Handles standard login forms; may not work with OAuth, SSO, or multi-factor authentication
- **CAPTCHAs**: Cannot bypass CAPTCHA challenges
- **Rate limiting**: May trigger rate limits on some sites
- **Same-domain only**: Exploration limited to starting domain

## Future Enhancements

Potential improvements:
- [ ] Integration with LLM APIs for enhanced AI reasoning
- [ ] Vision model integration for visual anomaly detection
- [ ] Support for multi-domain exploration
- [ ] HTML diff comparison for before/after states
- [ ] Interactive replay dashboard
- [ ] Custom plugin system
- [ ] Advanced authentication (OAuth, SSO, MFA)
- [ ] Performance metrics collection

## Contributing

This is a self-contained framework. To extend or modify:

1. Fork the codebase
2. Create feature branches
3. Add tests for new functionality
4. Submit pull requests

## License

This framework is provided as-is for educational and authorized testing purposes.

## Support

For issues, questions, or enhancements:
1. Check the troubleshooting section
2. Review execution logs in `logs/`
3. Examine the generated reports for insights

## Example Run

```bash
$ python main.py --url https://demo.testfire.net

================================================================================
AI-Driven Web Exploratory Testing Framework
================================================================================
Target URL: https://demo.testfire.net
Max Steps: 50
Max Depth: 3
Headless Mode: True
================================================================================
[INFO] Starting browser...
[INFO] Browser started successfully
[INFO] Starting exploration...
[INFO] Navigating to: https://demo.testfire.net
[INFO] Screenshot captured: step_001_click_login.png (245 KB)
[INFO] [Step 1] CLICK: Clicked element: Login
[INFO] Screenshot captured: step_002_input_username.png (238 KB)
[INFO] [Step 2] INPUT: Entered text: test@example.com
...
================================================================================
Exploration Complete!
Total Steps: 37
URLs Visited: 12
Duration: 2m 15s
================================================================================
[INFO] Generating PDF report...
================================================================================
✓ Report generated successfully!
✓ Report location: outputs/reports/exploration_report_demo_testfire_net_2025-11-08_14-23-45.pdf
================================================================================
```

## Credits

Built with:
- **Playwright** - Browser automation
- **FPDF2** - PDF generation
- **Python 3.11+** - Core language

---

**Made for intelligent, autonomous web exploration and testing.**
