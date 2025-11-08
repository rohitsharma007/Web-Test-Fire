"""
Screenshot agent for the web exploratory testing framework.
Captures visual evidence at each step and maintains screenshot metadata.
"""

import os
import json
import logging
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, asdict
from pathlib import Path
from core.browser_manager import BrowserManager
from core.utils import sanitize_filename, ensure_directory


@dataclass
class ScreenshotMetadata:
    """Metadata for a captured screenshot."""
    step_number: int
    filename: str
    filepath: str
    timestamp: str
    action_description: str
    url: str
    page_title: str = ""
    file_size_kb: int = 0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


class ScreenshotAgent:
    """
    Agent responsible for capturing screenshots and maintaining metadata.
    """

    def __init__(
        self,
        output_dir: str = "outputs/screenshots",
        full_page: bool = False,
        logger: Optional[logging.Logger] = None
    ):
        """
        Initialize screenshot agent.

        Args:
            output_dir: Directory to save screenshots
            full_page: Capture full page or just viewport
            logger: Logger instance
        """
        self.output_dir = ensure_directory(output_dir)
        self.full_page = full_page
        self.logger = logger or logging.getLogger(__name__)

        self.screenshots: List[ScreenshotMetadata] = []
        self.screenshot_count = 0

    def _generate_filename(self, step: int, action_description: str) -> str:
        """
        Generate filename for screenshot.

        Args:
            step: Step number
            action_description: Description of the action

        Returns:
            Sanitized filename
        """
        # Create descriptive filename
        sanitized_action = sanitize_filename(action_description, max_length=50)
        filename = f"step_{step:03d}_{sanitized_action}.png"
        return filename

    async def capture(
        self,
        browser: BrowserManager,
        step: int,
        action_description: str,
        timestamp: str
    ) -> Optional[ScreenshotMetadata]:
        """
        Capture a screenshot.

        Args:
            browser: Browser manager instance
            step: Current step number
            action_description: Description of the action
            timestamp: ISO timestamp

        Returns:
            ScreenshotMetadata if successful, None otherwise
        """
        try:
            # Generate filename
            filename = self._generate_filename(step, action_description)
            filepath = os.path.join(self.output_dir, filename)

            # Capture screenshot
            success = await browser.take_screenshot(filepath, full_page=self.full_page)

            if not success:
                self.logger.error(f"Failed to capture screenshot for step {step}")
                return None

            # Get current page info
            url = await browser.get_current_url()
            page_title = await browser.get_page_title()

            # Get file size
            file_size_kb = int(os.path.getsize(filepath) / 1024) if os.path.exists(filepath) else 0

            # Create metadata
            metadata = ScreenshotMetadata(
                step_number=step,
                filename=filename,
                filepath=filepath,
                timestamp=timestamp,
                action_description=action_description,
                url=url,
                page_title=page_title,
                file_size_kb=file_size_kb
            )

            self.screenshots.append(metadata)
            self.screenshot_count += 1

            self.logger.info(f"Screenshot captured: {filename} ({file_size_kb} KB)")

            return metadata

        except Exception as e:
            self.logger.error(f"Error capturing screenshot: {e}")
            return None

    def get_screenshot_metadata(self, step: int) -> Optional[ScreenshotMetadata]:
        """
        Get metadata for a specific step.

        Args:
            step: Step number

        Returns:
            ScreenshotMetadata if found, None otherwise
        """
        for metadata in self.screenshots:
            if metadata.step_number == step:
                return metadata
        return None

    def get_all_screenshots(self) -> List[ScreenshotMetadata]:
        """
        Get all screenshot metadata.

        Returns:
            List of screenshot metadata
        """
        return self.screenshots.copy()

    def export_metadata(self, filepath: str):
        """
        Export screenshot metadata to JSON file.

        Args:
            filepath: Path to output JSON file
        """
        try:
            data = {
                'total_screenshots': self.screenshot_count,
                'screenshots': [meta.to_dict() for meta in self.screenshots]
            }

            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            self.logger.info(f"Screenshot metadata exported to {filepath}")

        except Exception as e:
            self.logger.error(f"Failed to export metadata: {e}")

    def get_total_size_mb(self) -> float:
        """
        Get total size of all screenshots in megabytes.

        Returns:
            Total size in MB
        """
        total_kb = sum(meta.file_size_kb for meta in self.screenshots)
        return total_kb / 1024

    def cleanup_old_screenshots(self, keep_latest: int = 100):
        """
        Remove old screenshots, keeping only the latest N.

        Args:
            keep_latest: Number of latest screenshots to keep
        """
        if len(self.screenshots) <= keep_latest:
            return

        # Sort by step number
        sorted_screenshots = sorted(self.screenshots, key=lambda x: x.step_number)

        # Delete old screenshots
        to_delete = sorted_screenshots[:-keep_latest]

        for meta in to_delete:
            try:
                if os.path.exists(meta.filepath):
                    os.remove(meta.filepath)
                    self.logger.debug(f"Deleted old screenshot: {meta.filename}")
            except Exception as e:
                self.logger.warning(f"Failed to delete {meta.filename}: {e}")

        # Update list
        self.screenshots = sorted_screenshots[-keep_latest:]

    def __len__(self) -> int:
        """Get number of screenshots captured."""
        return self.screenshot_count
