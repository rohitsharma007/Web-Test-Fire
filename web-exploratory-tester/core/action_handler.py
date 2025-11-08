"""
Action handler module for the web exploratory testing framework.
Executes and validates UI interactions selected by the explorer agent.
"""

import logging
from typing import Dict, Any, Optional
from dataclasses import dataclass
from .browser_manager import BrowserManager


@dataclass
class ActionResult:
    """Result of an action execution."""
    success: bool
    action_type: str
    element_selector: str
    element_text: str
    url_before: str
    url_after: str
    error: Optional[str] = None
    notes: str = ""
    dom_changed: bool = False
    url_changed: bool = False


class ActionHandler:
    """
    Handles execution and validation of UI interactions.
    """

    # Sample data for form inputs
    SAMPLE_EMAILS = ['test@example.com', 'user@test.com', 'explorer@demo.com']
    SAMPLE_NAMES = ['John Doe', 'Jane Smith', 'Test User']
    SAMPLE_SEARCH_TERMS = ['test', 'search', 'demo', 'example']
    SAMPLE_PASSWORDS = ['Test123!', 'SecurePass123']
    SAMPLE_PHONE = ['555-0123', '555-1234']

    def __init__(
        self,
        browser_manager: BrowserManager,
        logger: Optional[logging.Logger] = None
    ):
        """
        Initialize action handler.

        Args:
            browser_manager: Browser manager instance
            logger: Logger instance
        """
        self.browser = browser_manager
        self.logger = logger or logging.getLogger(__name__)
        self.sample_email_index = 0
        self.sample_name_index = 0
        self.sample_search_index = 0

    async def execute_click(
        self,
        selector: str,
        element_text: str
    ) -> ActionResult:
        """
        Execute a click action.

        Args:
            selector: Element selector
            element_text: Element text content

        Returns:
            ActionResult with execution details
        """
        url_before = await self.browser.get_current_url()

        try:
            # Perform click
            success = await self.browser.click_element(selector)

            # Wait for any changes
            await self.browser.page.wait_for_timeout(1500)

            url_after = await self.browser.get_current_url()
            url_changed = url_before != url_after

            # Handle any popups that appeared
            if self.browser.popup_handler:
                popup_count = await self.browser.popup_handler.handle_all_popups(self.browser.page)
                if popup_count > 0:
                    self.logger.info(f"Handled {popup_count} popup(s) after click")

            return ActionResult(
                success=success,
                action_type='click',
                element_selector=selector,
                element_text=element_text,
                url_before=url_before,
                url_after=url_after,
                url_changed=url_changed,
                dom_changed=True,
                notes=f"Clicked element: {element_text[:50]}"
            )

        except Exception as e:
            return ActionResult(
                success=False,
                action_type='click',
                element_selector=selector,
                element_text=element_text,
                url_before=url_before,
                url_after=url_before,
                error=str(e),
                notes=f"Click failed: {e}"
            )

    async def execute_input(
        self,
        selector: str,
        element_text: str,
        input_type: str = 'text'
    ) -> ActionResult:
        """
        Execute an input action with appropriate sample data.

        Args:
            selector: Element selector
            element_text: Placeholder or label text
            input_type: Type of input field

        Returns:
            ActionResult with execution details
        """
        url_before = await self.browser.get_current_url()

        try:
            # Determine appropriate sample data
            sample_data = self._get_sample_data(element_text, input_type)

            # Perform input
            success = await self.browser.type_text(selector, sample_data)

            url_after = await self.browser.get_current_url()

            return ActionResult(
                success=success,
                action_type='input',
                element_selector=selector,
                element_text=element_text,
                url_before=url_before,
                url_after=url_after,
                url_changed=False,
                dom_changed=True,
                notes=f"Entered text: {sample_data}"
            )

        except Exception as e:
            return ActionResult(
                success=False,
                action_type='input',
                element_selector=selector,
                element_text=element_text,
                url_before=url_before,
                url_after=url_before,
                error=str(e),
                notes=f"Input failed: {e}"
            )

    async def execute_select(
        self,
        selector: str,
        element_text: str,
        option_value: str = ""
    ) -> ActionResult:
        """
        Execute a select dropdown action.

        Args:
            selector: Element selector
            element_text: Label text
            option_value: Option value to select (empty to select first)

        Returns:
            ActionResult with execution details
        """
        url_before = await self.browser.get_current_url()

        try:
            # If no option specified, try to get first non-empty option
            if not option_value:
                options = await self.browser.page.eval_on_selector(
                    selector,
                    'el => Array.from(el.options).map(opt => opt.value).filter(v => v)'
                )
                option_value = options[1] if len(options) > 1 else (options[0] if options else '')

            success = await self.browser.select_option(selector, option_value)

            url_after = await self.browser.get_current_url()

            return ActionResult(
                success=success,
                action_type='select',
                element_selector=selector,
                element_text=element_text,
                url_before=url_before,
                url_after=url_after,
                url_changed=False,
                dom_changed=True,
                notes=f"Selected option: {option_value}"
            )

        except Exception as e:
            return ActionResult(
                success=False,
                action_type='select',
                element_selector=selector,
                element_text=element_text,
                url_before=url_before,
                url_after=url_before,
                error=str(e),
                notes=f"Select failed: {e}"
            )

    async def execute_scroll(self, direction: str = 'down') -> ActionResult:
        """
        Execute a scroll action.

        Args:
            direction: 'down' or 'up'

        Returns:
            ActionResult with execution details
        """
        url_before = await self.browser.get_current_url()

        try:
            success = await self.browser.scroll_page(direction)

            url_after = await self.browser.get_current_url()

            return ActionResult(
                success=success,
                action_type='scroll',
                element_selector='window',
                element_text='',
                url_before=url_before,
                url_after=url_after,
                url_changed=False,
                dom_changed=False,
                notes=f"Scrolled {direction}"
            )

        except Exception as e:
            return ActionResult(
                success=False,
                action_type='scroll',
                element_selector='window',
                element_text='',
                url_before=url_before,
                url_after=url_before,
                error=str(e),
                notes=f"Scroll failed: {e}"
            )

    def _get_sample_data(self, element_text: str, input_type: str) -> str:
        """
        Get appropriate sample data based on input field context.

        Args:
            element_text: Placeholder or label text
            input_type: Input field type

        Returns:
            Sample data string
        """
        text_lower = element_text.lower()

        # Email fields
        if 'email' in text_lower or input_type == 'email':
            data = self.SAMPLE_EMAILS[self.sample_email_index % len(self.SAMPLE_EMAILS)]
            self.sample_email_index += 1
            return data

        # Name fields
        if any(keyword in text_lower for keyword in ['name', 'full name', 'username']):
            data = self.SAMPLE_NAMES[self.sample_name_index % len(self.SAMPLE_NAMES)]
            self.sample_name_index += 1
            return data

        # Password fields
        if 'password' in text_lower or input_type == 'password':
            return self.SAMPLE_PASSWORDS[0]

        # Phone fields
        if 'phone' in text_lower or 'tel' in text_lower:
            return self.SAMPLE_PHONE[0]

        # Search fields
        if 'search' in text_lower:
            data = self.SAMPLE_SEARCH_TERMS[self.sample_search_index % len(self.SAMPLE_SEARCH_TERMS)]
            self.sample_search_index += 1
            return data

        # Default text
        return 'Test input'

    def is_safe_action(self, element_text: str, action_type: str = 'click') -> bool:
        """
        Determine if an action is safe to perform.

        Args:
            element_text: Element text content
            action_type: Type of action

        Returns:
            True if safe, False otherwise
        """
        text_lower = element_text.lower()

        # Unsafe keywords
        unsafe_keywords = [
            'delete', 'remove', 'logout', 'log out', 'sign out',
            'cancel order', 'purchase', 'buy now', 'pay', 'checkout',
            'subscribe', 'unsubscribe', 'deactivate', 'close account'
        ]

        # Check for unsafe keywords
        for keyword in unsafe_keywords:
            if keyword in text_lower:
                self.logger.warning(f"Skipping unsafe action: {element_text}")
                return False

        return True

    async def validate_action_result(self, result: ActionResult) -> bool:
        """
        Validate that an action had the expected effect.

        Args:
            result: Action result to validate

        Returns:
            True if action appears successful, False otherwise
        """
        if not result.success:
            return False

        # For clicks that should navigate, check if URL changed
        if result.action_type == 'click':
            # If element text suggests navigation, expect URL change
            nav_keywords = ['next', 'continue', 'submit', 'go', 'proceed']
            suggests_navigation = any(
                keyword in result.element_text.lower()
                for keyword in nav_keywords
            )

            if suggests_navigation and not result.url_changed:
                self.logger.debug(f"Expected navigation but URL didn't change")
                # Still might be valid (modal, AJAX, etc.)

        return True
