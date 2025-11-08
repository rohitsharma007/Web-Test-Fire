# Quick Start Guide

Get started with the AI-Driven Web Exploratory Testing Framework in 5 minutes!

## Installation

### Step 1: Install Dependencies

```bash
# Navigate to the project directory
cd web-exploratory-tester

# Install Python packages
pip install -r requirements.txt

# Install Playwright browsers
playwright install chromium
```

### Step 2: Verify Installation

```bash
python main.py --help
```

You should see the help message with available options.

## First Test Run

### Example 1: Test a Demo Site

```bash
python main.py --url https://demo.testfire.net
```

This will:
1. Launch browser (headless)
2. Explore the website for up to 50 steps
3. Capture screenshots at each step
4. Generate a PDF report

**Expected output:**
```
Starting browser...
Starting exploration...
[Step 1] CLICK: Clicked element: Login
[Step 2] INPUT: Entered text: test@example.com
...
Exploration Complete!
✓ Report generated: outputs/reports/exploration_report_demo_testfire_net_[timestamp].pdf
```

### Example 2: Watch the Browser in Action

Want to see what's happening? Run with visible browser:

```bash
python main.py --url https://example.com --headless False
```

A browser window will open and you can watch the AI navigate the site!

### Example 3: Extended Exploration

For more thorough testing:

```bash
python main.py --url https://example.com --max-steps 100 --depth 5
```

## Understanding the Output

After running, check these directories:

### 1. Screenshots Directory
```
outputs/screenshots/
├── step_001_initial_page_load.png
├── step_002_click_login.png
├── step_003_input_email.png
└── ...
```

### 2. Reports Directory
```
outputs/reports/
└── exploration_report_example_com_2025-11-08_14-23-45.pdf
```

Open the PDF to see:
- Summary statistics
- Step-by-step actions with screenshots
- Observations and recommendations

### 3. Logs Directory
```
logs/
├── exploration.log          # Detailed execution log
├── session_data.json        # Complete interaction history
└── screenshot_metadata.json # Screenshot details
```

## Common Use Cases

### Testing a Login Flow

```bash
python main.py --url https://yoursite.com/login --max-steps 30
```

The framework will:
- Identify login form fields
- Fill in sample credentials
- Click login button
- Capture each step

### Exploring an E-commerce Site

```bash
python main.py --url https://yourshop.com --max-steps 100 --depth 4
```

The framework will:
- Navigate product categories
- Click on products
- Add items to cart (if safe)
- Explore checkout flow (without purchasing)

### Testing a Documentation Site

```bash
python main.py --url https://docs.yoursite.com --max-steps 75
```

The framework will:
- Click through documentation pages
- Test search functionality
- Navigate table of contents
- Verify links work

## Interpreting Results

### Successful Exploration

Look for in the log:
```
Exploration Complete!
Total Steps: 45
URLs Visited: 15
Duration: 3m 12s
```

### Common Findings

The PDF report may highlight:
- **Failed interactions**: Elements that couldn't be clicked
- **Popup handling**: Cookie banners and modals handled
- **Coverage**: Number of unique pages explored
- **Recommendations**: Suggestions based on findings

## Next Steps

1. **Review the PDF report** - Main insights and screenshots
2. **Check session_data.json** - Detailed interaction data
3. **Examine screenshots** - Visual verification of each step
4. **Review logs** - Debug any issues

## Tips for Better Results

### 1. Adjust Max Steps
- Small sites: `--max-steps 25`
- Medium sites: `--max-steps 50` (default)
- Large sites: `--max-steps 100+`

### 2. Set Appropriate Depth
- Single-page apps: `--depth 1`
- Standard sites: `--depth 3` (default)
- Complex sites: `--depth 5+`

### 3. Use Headless Mode
- Development: `--headless False` (watch it work)
- Production/CI: `--headless True` (faster)

## Troubleshooting Quick Fixes

### Issue: "Command not found"
```bash
# Make sure you're in the right directory
cd web-exploratory-tester

# Use python3 if python doesn't work
python3 main.py --url https://example.com
```

### Issue: "playwright not installed"
```bash
pip install playwright
playwright install chromium
```

### Issue: "No screenshots generated"
Check:
1. Directory permissions: `ls -la outputs/screenshots/`
2. Disk space: `df -h`
3. Log file: `cat logs/exploration.log`

### Issue: "PDF not generated"
```bash
# Reinstall fpdf2
pip install --upgrade fpdf2
```

## Advanced Configuration

### Running Multiple Tests

Create a shell script:
```bash
#!/bin/bash
# test_suite.sh

python main.py --url https://site1.com --max-steps 50
python main.py --url https://site2.com --max-steps 50
python main.py --url https://site3.com --max-steps 50

echo "All tests complete!"
```

Run it:
```bash
chmod +x test_suite.sh
./test_suite.sh
```

### Scheduling Regular Tests

Use cron (Linux/Mac):
```bash
# Edit crontab
crontab -e

# Add line to run daily at 2 AM
0 2 * * * cd /path/to/web-exploratory-tester && python main.py --url https://yoursite.com
```

## Getting Help

1. **Check the README.md** - Full documentation
2. **Review logs** - `logs/exploration.log`
3. **Examine examples** - This guide's examples
4. **Modify code** - Framework is fully customizable

## Example Complete Workflow

```bash
# 1. Run exploration
python main.py --url https://demo.testfire.net --max-steps 50

# 2. Check the report
open outputs/reports/exploration_report_*.pdf
# (or use 'xdg-open' on Linux, 'start' on Windows)

# 3. Review screenshots
ls -lh outputs/screenshots/

# 4. Check for errors
grep ERROR logs/exploration.log

# 5. View interaction data
cat logs/session_data.json | python -m json.tool | less
```

## You're Ready!

Start exploring websites intelligently:

```bash
python main.py --url YOUR_URL_HERE
```

Happy testing! 🚀
