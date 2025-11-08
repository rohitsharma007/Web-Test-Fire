"""
Explorer agent for the web exploratory testing framework.
Core decision-making brain that intelligently explores web pages using AI reasoning.
"""

import logging
import random
from typing import Optional, Dict, Any, List
from core.browser_manager import BrowserManager
from core.action_handler import ActionHandler, ActionResult
from core.state_tracker import StateTracker
from core.utils import get_iso_timestamp
from agents.screenshot_agent import ScreenshotAgent


class ExplorerAgent:
    """
    AI-powered agent that explores web applications intelligently.
    Makes decisions about which elements to interact with and how.
    """

    # Element priorities for exploration
    PRIORITY_KEYWORDS = {
        'high': ['login', 'sign in', 'get started', 'start', 'begin', 'enter', 'continue', 'next', 'search', 'submit'],
        'medium': ['register', 'sign up', 'learn more', 'view', 'show', 'explore', 'browse', 'menu'],
        'low': ['about', 'contact', 'help', 'support', 'faq', 'terms', 'privacy', 'blog']
    }

    # Keywords to skip
    SKIP_KEYWORDS = [
        'logout', 'log out', 'sign out', 'delete', 'remove', 'cancel',
        'purchase', 'buy', 'checkout', 'pay', 'subscribe', 'download pdf',
        'download zip', 'unsubscribe'
    ]

    def __init__(
        self,
        browser: BrowserManager,
        state_tracker: StateTracker,
        screenshot_agent: ScreenshotAgent,
        max_steps: int = 50,
        logger: Optional[logging.Logger] = None
    ):
        """
        Initialize explorer agent.

        Args:
            browser: Browser manager instance
            state_tracker: State tracker instance
            screenshot_agent: Screenshot agent instance
            max_steps: Maximum exploration steps
            logger: Logger instance
        """
        self.browser = browser
        self.state_tracker = state_tracker
        self.screenshot_agent = screenshot_agent
        self.max_steps = max_steps
        self.logger = logger or logging.getLogger(__name__)

        self.action_handler = ActionHandler(browser, logger)
        self.exploration_complete = False

    async def explore(self, url: str) -> bool:
        """
        Start exploration from a URL.

        Args:
            url: Starting URL

        Returns:
            True if exploration completed successfully
        """
        try:
            self.logger.info(f"Starting exploration of: {url}")

            # Navigate to URL
            success = await self.browser.navigate(url)
            if not success:
                self.logger.error("Failed to navigate to starting URL")
                return False

            # Capture initial screenshot
            await self.screenshot_agent.capture(
                self.browser,
                step=0,
                action_description="initial_page_load",
                timestamp=get_iso_timestamp()
            )

            # Record initial state
            self.state_tracker.record_interaction(
                action_type='navigate',
                element_selector='browser',
                element_text='Initial navigation',
                url_before='',
                url_after=url,
                screenshot_path=None,
                notes=f"Started exploration at {url}",
                success=True
            )

            # Main exploration loop
            await self._exploration_loop()

            self.logger.info("Exploration completed")
            return True

        except Exception as e:
            self.logger.error(f"Exploration failed: {e}")
            return False

    async def _exploration_loop(self):
        """Main exploration loop."""
        consecutive_failures = 0
        max_consecutive_failures = 5

        while self.state_tracker.current_step < self.max_steps:
            try:
                # Check if we should continue
                if consecutive_failures >= max_consecutive_failures:
                    self.logger.warning("Too many consecutive failures, stopping exploration")
                    break

                # Get visible elements
                elements = await self.browser.get_visible_elements()

                if not elements:
                    self.logger.info("No more visible elements to interact with")
                    break

                # Select best action
                action = await self._select_next_action(elements)

                if not action:
                    self.logger.info("No suitable action found, exploration complete")
                    break

                # Execute action
                result = await self._execute_action(action)

                # Record interaction
                screenshot_path = None
                if result.success:
                    consecutive_failures = 0

                    # Capture screenshot
                    screenshot_meta = await self.screenshot_agent.capture(
                        self.browser,
                        step=self.state_tracker.current_step + 1,
                        action_description=action['description'],
                        timestamp=get_iso_timestamp()
                    )
                    if screenshot_meta:
                        screenshot_path = screenshot_meta.filepath

                else:
                    consecutive_failures += 1

                # Record in state tracker
                self.state_tracker.record_interaction(
                    action_type=result.action_type,
                    element_selector=result.element_selector,
                    element_text=result.element_text,
                    url_before=result.url_before,
                    url_after=result.url_after,
                    screenshot_path=screenshot_path,
                    notes=result.notes,
                    success=result.success,
                    error=result.error
                )

                # Log progress
                self.logger.info(
                    f"[Step {self.state_tracker.current_step}] "
                    f"{result.action_type.upper()}: {result.notes}"
                )

                # Small delay between actions
                await self.browser.page.wait_for_timeout(1000)

            except Exception as e:
                self.logger.error(f"Error in exploration loop: {e}")
                consecutive_failures += 1

        self.exploration_complete = True

    async def _select_next_action(self, elements: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """
        Select the best next action from available elements using AI-like reasoning.

        Args:
            elements: List of visible elements

        Returns:
            Action dictionary or None if no suitable action
        """
        # Filter out already interacted elements and unsafe actions
        candidate_elements = []

        for element in elements:
            element_id = self.state_tracker.create_element_id(
                element['selector'],
                element['text']
            )

            # Skip if already interacted
            if self.state_tracker.has_interacted_with_element(element_id):
                continue

            # Skip if unsafe
            if not self.action_handler.is_safe_action(element['text']):
                continue

            # Skip if contains skip keywords
            if self._should_skip_element(element['text']):
                continue

            # Add priority score
            element['priority'] = self._calculate_priority(element)
            candidate_elements.append(element)

        if not candidate_elements:
            return None

        # Sort by priority
        candidate_elements.sort(key=lambda x: x['priority'], reverse=True)

        # Select top candidate with some randomness for variety
        # 70% chance to pick highest priority, 30% chance for variety
        if random.random() < 0.7:
            selected = candidate_elements[0]
        else:
            # Pick from top 3
            top_n = min(3, len(candidate_elements))
            selected = random.choice(candidate_elements[:top_n])

        # Determine action type
        action = self._create_action(selected)

        return action

    def _calculate_priority(self, element: Dict[str, Any]) -> float:
        """
        Calculate priority score for an element.

        Args:
            element: Element dictionary

        Returns:
            Priority score (higher is better)
        """
        text = element['text'].lower()
        tag = element['tag']
        element_type = element.get('type', '')

        score = 0.0

        # Base scores by tag
        if tag == 'button' or element_type == 'submit':
            score += 10
        elif tag == 'a':
            score += 8
        elif tag == 'input':
            score += 7
        elif tag == 'select':
            score += 6

        # Keyword-based priority
        for keyword in self.PRIORITY_KEYWORDS['high']:
            if keyword in text:
                score += 15

        for keyword in self.PRIORITY_KEYWORDS['medium']:
            if keyword in text:
                score += 10

        for keyword in self.PRIORITY_KEYWORDS['low']:
            if keyword in text:
                score += 5

        # Prefer elements with clear text
        if text and len(text.strip()) > 0:
            score += 5

        # Prefer links that look like they navigate
        if tag == 'a' and element.get('href'):
            href = element['href']
            if self.state_tracker.should_explore_url(href):
                score += 10
            else:
                score -= 20  # Already visited or external

        # Small random factor for variety
        score += random.uniform(0, 2)

        return score

    def _should_skip_element(self, text: str) -> bool:
        """
        Check if element should be skipped.

        Args:
            text: Element text

        Returns:
            True if should skip, False otherwise
        """
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in self.SKIP_KEYWORDS)

    def _create_action(self, element: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create action dictionary from element.

        Args:
            element: Element dictionary

        Returns:
            Action dictionary
        """
        tag = element['tag']
        element_type = element.get('type', '')
        text = element['text']
        selector = element['selector']

        # Determine action type
        if tag == 'input' and element_type in ['text', 'email', 'search', 'tel', 'password']:
            action_type = 'input'
            description = f"input_{text or element_type}"
        elif tag == 'select':
            action_type = 'select'
            description = f"select_{text}"
        else:
            action_type = 'click'
            description = f"click_{text or tag}"

        return {
            'type': action_type,
            'element': element,
            'selector': selector,
            'text': text,
            'description': description
        }

    async def _execute_action(self, action: Dict[str, Any]) -> ActionResult:
        """
        Execute the selected action.

        Args:
            action: Action dictionary

        Returns:
            ActionResult
        """
        action_type = action['type']
        selector = action['selector']
        text = action['text']
        element = action['element']

        if action_type == 'click':
            return await self.action_handler.execute_click(selector, text)
        elif action_type == 'input':
            input_type = element.get('type', 'text')
            return await self.action_handler.execute_input(selector, text, input_type)
        elif action_type == 'select':
            return await self.action_handler.execute_select(selector, text)
        else:
            # Default to click
            return await self.action_handler.execute_click(selector, text)

    def get_summary(self) -> Dict[str, Any]:
        """
        Get exploration summary.

        Returns:
            Summary dictionary
        """
        return self.state_tracker.get_summary()
