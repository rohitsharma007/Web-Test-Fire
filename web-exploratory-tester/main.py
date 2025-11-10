#!/usr/bin/env python3
"""
Main entry point for the AI-driven Web Exploratory Testing Framework.

This tool autonomously explores web applications, interacts intelligently with UI elements,
captures screenshots, and generates comprehensive PDF reports.

Usage:
    python main.py --url https://example.com
    python main.py --url https://example.com --max-steps 100 --depth 5
    python main.py --url https://example.com --headless False
"""

import asyncio
import argparse
import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from core.browser_manager import BrowserManager
from core.state_tracker import StateTracker
from core.utils import setup_logger, format_duration, ensure_directory
from agents.explorer_agent import ExplorerAgent
from agents.screenshot_agent import ScreenshotAgent
from agents.report_agent import ReportAgent


class WebExploratoryTester:
    """
    Main orchestrator for the web exploratory testing framework.
    """

    def __init__(
        self,
        url: str,
        max_steps: int = 50,
        depth: int = 3,
        headless: bool = True,
        output_base: str = "outputs"
    ):
        """
        Initialize the tester.

        Args:
            url: Target URL to explore
            max_steps: Maximum number of exploration steps
            depth: Maximum depth of navigation from base URL
            headless: Run browser in headless mode
            output_base: Base directory for outputs
        """
        self.url = url
        self.max_steps = max_steps
        self.depth = depth
        self.headless = headless

        # Set up directories
        self.output_base = ensure_directory(output_base)
        self.screenshot_dir = ensure_directory(os.path.join(output_base, "screenshots"))
        self.report_dir = ensure_directory(os.path.join(output_base, "reports"))
        self.log_dir = ensure_directory("logs")

        # Set up logging
        log_file = os.path.join(self.log_dir, "exploration.log")
        self.logger = setup_logger("WebExploratoryTester", log_file)

        # Components
        self.browser = None
        self.state_tracker = None
        self.screenshot_agent = None
        self.explorer_agent = None
        self.report_agent = None

    async def run(self) -> bool:
        """
        Run the complete exploration and reporting workflow.

        Returns:
            True if successful, False otherwise
        """
        try:
            self.logger.info("=" * 80)
            self.logger.info("AI-Driven Web Exploratory Testing Framework")
            self.logger.info("=" * 80)
            self.logger.info(f"Target URL: {self.url}")
            self.logger.info(f"Max Steps: {self.max_steps}")
            self.logger.info(f"Max Depth: {self.depth}")
            self.logger.info(f"Headless Mode: {self.headless}")
            self.logger.info("=" * 80)

            # Initialize components
            await self._initialize_components()

            # Start browser
            self.logger.info("Starting browser...")
            await self.browser.start()

            # Run exploration
            self.logger.info("Starting exploration...")
            success = await self.explorer_agent.explore(self.url)

            if not success:
                self.logger.error("Exploration failed")
                return False

            # Get summary
            summary = self.explorer_agent.get_summary()
            self.logger.info("=" * 80)
            self.logger.info("Exploration Complete!")
            self.logger.info(f"Total Steps: {summary['total_steps']}")
            self.logger.info(f"URLs Visited: {summary['total_urls_visited']}")
            self.logger.info(f"Duration: {format_duration(summary['session_duration_seconds'])}")
            self.logger.info("=" * 80)

            # Export session data
            session_file = os.path.join(self.log_dir, "session_data.json")
            self.state_tracker.export_to_json(session_file)
            self.logger.info(f"Session data exported to: {session_file}")

            # Export screenshot metadata
            screenshot_meta_file = os.path.join(self.log_dir, "screenshot_metadata.json")
            self.screenshot_agent.export_metadata(screenshot_meta_file)

            # Generate report
            self.logger.info("Generating PDF report...")
            report_path = self.report_agent.generate(
                self.state_tracker,
                self.screenshot_agent
            )

            if report_path:
                self.logger.info("=" * 80)
                self.logger.info(f"✓ Report generated successfully!")
                self.logger.info(f"✓ Report location: {report_path}")
                self.logger.info("=" * 80)
            else:
                self.logger.error("Failed to generate report")
                return False

            return True

        except KeyboardInterrupt:
            self.logger.warning("Exploration interrupted by user")
            return False

        except Exception as e:
            self.logger.error(f"Error during exploration: {e}", exc_info=True)
            return False

        finally:
            # Cleanup
            await self._cleanup()

    async def _initialize_components(self):
        """Initialize all components."""
        # Browser manager
        self.browser = BrowserManager(
            headless=self.headless,
            logger=self.logger
        )

        # State tracker
        self.state_tracker = StateTracker(
            base_url=self.url,
            max_depth=self.depth
        )

        # Screenshot agent
        self.screenshot_agent = ScreenshotAgent(
            output_dir=self.screenshot_dir,
            full_page=False,
            logger=self.logger
        )

        # Explorer agent
        self.explorer_agent = ExplorerAgent(
            browser=self.browser,
            state_tracker=self.state_tracker,
            screenshot_agent=self.screenshot_agent,
            max_steps=self.max_steps,
            logger=self.logger
        )

        # Report agent
        self.report_agent = ReportAgent(
            output_dir=self.report_dir,
            logger=self.logger
        )

    async def _cleanup(self):
        """Cleanup resources."""
        if self.browser:
            self.logger.info("Closing browser...")
            await self.browser.close()


def parse_arguments():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="AI-Driven Web Exploratory Testing Framework",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py --url https://example.com
  python main.py --url https://example.com --max-steps 100 --depth 5
  python main.py --url https://example.com --headless False

For more information, see README.md
        """
    )

    parser.add_argument(
        '--url',
        type=str,
        required=True,
        help='Target URL to explore (required)'
    )

    parser.add_argument(
        '--max-steps',
        type=int,
        default=50,
        help='Maximum number of exploration steps (default: 50)'
    )

    parser.add_argument(
        '--depth',
        type=int,
        default=3,
        help='Maximum depth of navigation from base URL (default: 3)'
    )

    parser.add_argument(
        '--headless',
        type=lambda x: x.lower() in ('true', '1', 'yes'),
        default=False,
        help='Run browser in headless mode (default: False)'
    )

    parser.add_argument(
        '--output',
        type=str,
        default='outputs',
        help='Base directory for outputs (default: outputs)'
    )

    return parser.parse_args()


async def main():
    """Main entry point."""
    # Parse arguments
    args = parse_arguments()

    # Validate URL
    if not args.url.startswith(('http://', 'https://')):
        print("Error: URL must start with http:// or https://")
        sys.exit(1)

    # Create tester instance
    tester = WebExploratoryTester(
        url=args.url,
        max_steps=args.max_steps,
        depth=args.depth,
        headless=args.headless,
        output_base=args.output
    )

    # Run exploration
    success = await tester.run()

    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    # Run async main
    asyncio.run(main())
