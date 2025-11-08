"""
State tracking module for the web exploratory testing framework.
Maintains session memory, tracks visited URLs, interacted elements, and prevents repetition.
"""

import json
from typing import Dict, List, Set, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime
from urllib.parse import urlparse, parse_qs


@dataclass
class InteractionRecord:
    """Record of a single interaction with a web element."""
    step_id: int
    timestamp: str
    action_type: str  # 'click', 'input', 'select', 'navigate', etc.
    element_selector: str
    element_text: str
    url_before: str
    url_after: str
    screenshot_path: Optional[str] = None
    notes: str = ""
    success: bool = True
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)


class StateTracker:
    """
    Tracks the state of the exploration session.
    Maintains memory of visited URLs, interacted elements, and session history.
    """

    def __init__(self, base_url: str, max_depth: int = 3):
        """
        Initialize the state tracker.

        Args:
            base_url: The starting URL for exploration
            max_depth: Maximum depth of navigation from base URL
        """
        self.base_url = base_url
        self.base_domain = self._extract_domain(base_url)
        self.max_depth = max_depth

        # Tracking sets
        self.visited_urls: Set[str] = set()
        self.visited_url_patterns: Set[str] = set()
        self.interacted_elements: Set[str] = set()

        # Session data
        self.interaction_history: List[InteractionRecord] = []
        self.current_step = 0
        self.current_url = base_url
        self.current_depth = 0
        self.session_start_time = datetime.now()

        # Statistics
        self.total_clicks = 0
        self.total_inputs = 0
        self.total_navigations = 0
        self.total_popups_handled = 0
        self.total_errors = 0

    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL."""
        parsed = urlparse(url)
        return parsed.netloc

    def _normalize_url(self, url: str) -> str:
        """
        Normalize URL by removing fragments and sorting query parameters.
        This helps identify effectively duplicate URLs.
        """
        parsed = urlparse(url)
        # Remove fragment
        normalized = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"

        # Sort query parameters to normalize
        if parsed.query:
            query_params = parse_qs(parsed.query)
            sorted_params = sorted(query_params.items())
            query_string = "&".join(f"{k}={v[0]}" for k, v in sorted_params)
            normalized += f"?{query_string}"

        return normalized

    def _create_url_pattern(self, url: str) -> str:
        """
        Create a pattern from URL by removing dynamic segments.
        Helps identify similar pages (e.g., product/123 and product/456).
        """
        parsed = urlparse(url)
        # Replace numbers with placeholder
        import re
        path_pattern = re.sub(r'\d+', '{id}', parsed.path)
        return f"{parsed.netloc}{path_pattern}"

    def has_visited_url(self, url: str) -> bool:
        """Check if URL has been visited."""
        normalized = self._normalize_url(url)
        return normalized in self.visited_urls

    def has_visited_similar_url(self, url: str) -> bool:
        """Check if a similar URL pattern has been visited."""
        pattern = self._create_url_pattern(url)
        return pattern in self.visited_url_patterns

    def mark_url_visited(self, url: str):
        """Mark a URL as visited."""
        normalized = self._normalize_url(url)
        pattern = self._create_url_pattern(url)
        self.visited_urls.add(normalized)
        self.visited_url_patterns.add(pattern)
        self.current_url = url

    def has_interacted_with_element(self, element_id: str) -> bool:
        """Check if element has been interacted with."""
        return element_id in self.interacted_elements

    def mark_element_interacted(self, element_id: str):
        """Mark an element as interacted with."""
        self.interacted_elements.add(element_id)

    def create_element_id(self, selector: str, text: str) -> str:
        """
        Create a unique identifier for an element.

        Args:
            selector: CSS selector or element locator
            text: Visible text of the element

        Returns:
            Unique element identifier
        """
        # Combine selector and text to create unique ID
        return f"{selector}::{text[:50]}"

    def record_interaction(
        self,
        action_type: str,
        element_selector: str,
        element_text: str,
        url_before: str,
        url_after: str,
        screenshot_path: Optional[str] = None,
        notes: str = "",
        success: bool = True,
        error: Optional[str] = None
    ) -> InteractionRecord:
        """
        Record a new interaction.

        Args:
            action_type: Type of action performed
            element_selector: Element selector
            element_text: Element text content
            url_before: URL before action
            url_after: URL after action
            screenshot_path: Path to screenshot
            notes: Additional notes
            success: Whether action succeeded
            error: Error message if failed

        Returns:
            Created interaction record
        """
        self.current_step += 1

        # Update statistics
        if action_type == 'click':
            self.total_clicks += 1
        elif action_type == 'input':
            self.total_inputs += 1
        elif action_type == 'navigate':
            self.total_navigations += 1
        elif action_type == 'popup':
            self.total_popups_handled += 1

        if not success:
            self.total_errors += 1

        # Create record
        record = InteractionRecord(
            step_id=self.current_step,
            timestamp=datetime.now().isoformat(),
            action_type=action_type,
            element_selector=element_selector,
            element_text=element_text,
            url_before=url_before,
            url_after=url_after,
            screenshot_path=screenshot_path,
            notes=notes,
            success=success,
            error=error
        )

        self.interaction_history.append(record)

        # Mark as visited/interacted
        element_id = self.create_element_id(element_selector, element_text)
        self.mark_element_interacted(element_id)
        self.mark_url_visited(url_after)

        return record

    def get_session_duration(self) -> float:
        """Get session duration in seconds."""
        return (datetime.now() - self.session_start_time).total_seconds()

    def is_same_domain(self, url: str) -> bool:
        """Check if URL is from the same domain as base URL."""
        return self._extract_domain(url) == self.base_domain

    def should_explore_url(self, url: str) -> bool:
        """
        Determine if a URL should be explored.

        Args:
            url: URL to check

        Returns:
            True if should explore, False otherwise
        """
        # Don't explore if already visited
        if self.has_visited_url(url):
            return False

        # Don't explore if it's a similar pattern and we've seen many
        if self.has_visited_similar_url(url) and len(self.visited_urls) > 10:
            return False

        # Don't explore external domains
        if not self.is_same_domain(url):
            return False

        # Skip certain file types
        skip_extensions = ['.pdf', '.zip', '.exe', '.dmg', '.jpg', '.png', '.gif']
        if any(url.lower().endswith(ext) for ext in skip_extensions):
            return False

        return True

    def get_summary(self) -> Dict[str, Any]:
        """
        Get session summary statistics.

        Returns:
            Dictionary with summary data
        """
        return {
            'base_url': self.base_url,
            'total_steps': self.current_step,
            'total_urls_visited': len(self.visited_urls),
            'total_clicks': self.total_clicks,
            'total_inputs': self.total_inputs,
            'total_navigations': self.total_navigations,
            'total_popups_handled': self.total_popups_handled,
            'total_errors': self.total_errors,
            'session_duration_seconds': self.get_session_duration(),
            'max_depth': self.max_depth,
            'current_depth': self.current_depth
        }

    def export_to_json(self, filepath: str):
        """
        Export session data to JSON file.

        Args:
            filepath: Path to output JSON file
        """
        data = {
            'summary': self.get_summary(),
            'interactions': [record.to_dict() for record in self.interaction_history],
            'visited_urls': list(self.visited_urls)
        }

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def get_last_interaction(self) -> Optional[InteractionRecord]:
        """Get the last interaction record."""
        return self.interaction_history[-1] if self.interaction_history else None

    def get_successful_interactions(self) -> List[InteractionRecord]:
        """Get all successful interactions."""
        return [r for r in self.interaction_history if r.success]

    def get_failed_interactions(self) -> List[InteractionRecord]:
        """Get all failed interactions."""
        return [r for r in self.interaction_history if not r.success]
