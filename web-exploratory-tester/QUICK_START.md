# Quick Start Guide - macOS

## Python Version Requirement

**IMPORTANT:** Use Python 3.11 instead of Python 3.14

Python 3.14 is very new and some dependencies (greenlet, playwright) don't have compatible builds yet. This framework works perfectly with Python 3.11.

## Installation Steps

1. **Install dependencies with Python 3.11:**
   ```bash
   cd web-exploratory-tester
   python3.11 -m pip install -r requirements.txt
   ```

2. **Install Playwright browser:**
   ```bash
   python3.11 -m playwright install chromium
   ```

## Running the Framework

### Basic Usage with Python 3.11

```bash
python3.11 main.py --url https://example.com
```

### With Automatic Login (OrangeHRM Demo)

```bash
python3.11 main.py --url https://opensource-demo.orangehrmlive.com \
  --username Admin --password admin123 --max-steps 25
```

### Extended Exploration

```bash
python3.11 main.py --url https://example.com \
  --max-steps 100 --depth 5 --headless True
```

## Recent Fixes (Completed)

### ✅ Browser Crash Issue - FIXED
**Problem:** "Target page, context or browser has been closed" and "Target crashed" errors

**Solution:** Enhanced browser launch with stability options:
- Single-process mode to prevent multi-process crashes
- Disabled sandboxing for compatibility
- Additional hardware acceleration disabling
- Improved crash detection and retry logic

**Test Result:** Screenshot capture and navigation now work without crashes!

### ✅ Automatic Login - IMPLEMENTED
The framework now intelligently:
- Detects login pages by analyzing URL, title, and form elements
- Finds username/password fields automatically
- Fills credentials and submits the form
- Verifies login success before continuing exploration

## Example Output

```bash
$ python3.11 main.py --url http://example.com --max-steps 3 --headless True

[INFO] ================================================================================
[INFO] AI-Driven Web Exploratory Testing Framework
[INFO] ================================================================================
[INFO] Target URL: http://example.com
[INFO] Max Steps: 3
[INFO] Max Depth: 3
[INFO] Headless Mode: True
[INFO] ================================================================================
[INFO] Starting browser...
[INFO] Browser started successfully
[INFO] Starting exploration...
[INFO] Starting exploration of: http://example.com
[INFO] Navigating to: http://example.com
[INFO] Successfully navigated to: http://example.com
[INFO] Screenshot captured: step_000_initial_page_load.png (11 KB)
[INFO] No more visible elements to interact with
[INFO] Exploration completed
[INFO] ================================================================================
```

## Outputs

After running, check these locations:

- **Screenshots:** `outputs/screenshots/`
- **PDF Reports:** `outputs/reports/`
- **Session Data:** `logs/session_data.json`
- **Execution Logs:** `logs/exploration.log`

## Troubleshooting

### If you get "ModuleNotFoundError"
Make sure you're using Python 3.11:
```bash
python3.11 -m pip install -r requirements.txt
```

### If you get "playwright not found"
Install Playwright browsers:
```bash
python3.11 -m playwright install chromium
```

### If browser fails to start in non-headless mode
On systems without a display server, always use `--headless True`:
```bash
python3.11 main.py --url https://example.com --headless True
```

## Network Connectivity

If testing sites that require internet access (like OrangeHRM demo), ensure your network allows HTTPS connections. Some restricted environments may block external sites.

For local testing, use:
- Local development servers
- Internal applications
- Sites accessible within your network

---

**Ready to explore!** 🚀

Use Python 3.11 and the framework will work perfectly with all the latest features including intelligent automatic login detection.
