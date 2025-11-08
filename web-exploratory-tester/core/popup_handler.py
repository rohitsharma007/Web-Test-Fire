"""
Popup and modal handler for the web exploratory testing framework.
Automatically detects and handles dialogs, modals, cookie banners, and permission requests.
"""

import re
import logging
from typing import Optional, List, Dict, Any
from playwright.async_api import Page, Dialog


class PopupHandler:
    """
    Handles various types of popups, modals, and dialogs encountered during exploration.
    """

    # Keywords indicating safe actions to accept
    SAFE_ACCEPT_KEYWORDS = [
        'accept', 'agree', 'allow', 'ok', 'continue', 'proceed', 'confirm',
        'yes', 'enable', 'got it', 'understand', 'close', 'dismiss',
        'accept cookies', 'accept all', 'i agree', 'consent'
    ]

    # Keywords indicating unsafe/destructive actions to skip
    UNSAFE_KEYWORDS = [
        'delete', 'remove', 'logout', 'log out', 'sign out', 'cancel order',
        'purchase', 'buy now', 'pay', 'subscribe', 'unsubscribe', 'deactivate'
    ]

    # Common modal selectors
    MODAL_SELECTORS = [
        '[role="dialog"]',
        '[role="alertdialog"]',
        '.modal',
        '.popup',
        '#modal',
        '.overlay',
        '[class*="modal"]',
        '[class*="popup"]',
        '[class*="dialog"]'
    ]

    # Cookie consent selectors
    COOKIE_BANNER_SELECTORS = [
        '#cookie-banner',
        '.cookie-banner',
        '[class*="cookie"]',
        '[class*="consent"]',
        '[id*="cookie"]',
        '[id*="consent"]',
        '[aria-label*="cookie"]',
        '[aria-label*="consent"]'
    ]

    def __init__(self, logger: Optional[logging.Logger] = None):
        """
        Initialize popup handler.

        Args:
            logger: Logger instance for logging popup interactions
        """
        self.logger = logger or logging.getLogger(__name__)
        self.handled_popups: List[Dict[str, Any]] = []

    async def setup_dialog_handler(self, page: Page):
        """
        Set up automatic dialog (alert/confirm/prompt) handler.

        Args:
            page: Playwright page instance
        """
        async def dialog_handler(dialog: Dialog):
            """Handle browser dialogs automatically."""
            message = dialog.message
            dialog_type = dialog.type

            self.logger.info(f"Dialog detected: [{dialog_type}] {message}")

            # Determine if safe to accept
            should_accept = self._is_safe_dialog(message)

            if should_accept:
                await dialog.accept()
                self.logger.info(f"Dialog accepted: {message}")
                self.handled_popups.append({
                    'type': 'dialog',
                    'subtype': dialog_type,
                    'message': message,
                    'action': 'accepted'
                })
            else:
                await dialog.dismiss()
                self.logger.warning(f"Dialog dismissed (unsafe): {message}")
                self.handled_popups.append({
                    'type': 'dialog',
                    'subtype': dialog_type,
                    'message': message,
                    'action': 'dismissed'
                })

        page.on("dialog", dialog_handler)

    def _is_safe_dialog(self, message: str) -> bool:
        """
        Determine if a dialog message is safe to accept.

        Args:
            message: Dialog message text

        Returns:
            True if safe to accept, False otherwise
        """
        message_lower = message.lower()

        # Check for unsafe keywords first
        for keyword in self.UNSAFE_KEYWORDS:
            if keyword in message_lower:
                return False

        # Check for safe keywords
        for keyword in self.SAFE_ACCEPT_KEYWORDS:
            if keyword in message_lower:
                return True

        # Default to dismissing if uncertain
        return False

    async def handle_cookie_consent(self, page: Page) -> bool:
        """
        Attempt to handle cookie consent banners.

        Args:
            page: Playwright page instance

        Returns:
            True if cookie banner was handled, False otherwise
        """
        try:
            # Wait a bit for cookie banners to appear
            await page.wait_for_timeout(1000)

            # Try to find cookie banner
            for selector in self.COOKIE_BANNER_SELECTORS:
                try:
                    banner = await page.query_selector(selector)
                    if banner and await banner.is_visible():
                        # Found cookie banner, try to accept
                        accepted = await self._accept_cookie_banner(page, banner)
                        if accepted:
                            self.logger.info(f"Cookie banner handled: {selector}")
                            self.handled_popups.append({
                                'type': 'cookie_banner',
                                'selector': selector,
                                'action': 'accepted'
                            })
                            return True
                except Exception:
                    continue

            return False

        except Exception as e:
            self.logger.error(f"Error handling cookie consent: {e}")
            return False

    async def _accept_cookie_banner(self, page: Page, banner) -> bool:
        """
        Try to click the accept button on a cookie banner.

        Args:
            page: Playwright page instance
            banner: Banner element

        Returns:
            True if successfully accepted, False otherwise
        """
        # Common accept button selectors
        accept_button_selectors = [
            'button:has-text("Accept")',
            'button:has-text("Agree")',
            'button:has-text("Allow")',
            'button:has-text("OK")',
            'button:has-text("I agree")',
            'button:has-text("Accept all")',
            'a:has-text("Accept")',
            'a:has-text("Agree")',
            '[id*="accept"]',
            '[class*="accept"]',
            '[aria-label*="accept"]'
        ]

        for selector in accept_button_selectors:
            try:
                button = await page.query_selector(selector)
                if button and await button.is_visible():
                    await button.click()
                    await page.wait_for_timeout(500)
                    return True
            except Exception:
                continue

        return False

    async def handle_modal(self, page: Page) -> Optional[Dict[str, Any]]:
        """
        Detect and handle modal dialogs.

        Args:
            page: Playwright page instance

        Returns:
            Dictionary with modal info if handled, None otherwise
        """
        try:
            for selector in self.MODAL_SELECTORS:
                try:
                    modal = await page.query_selector(selector)
                    if modal and await modal.is_visible():
                        # Found modal, try to close it
                        result = await self._close_modal(page, modal)
                        if result:
                            self.logger.info(f"Modal handled: {selector}")
                            self.handled_popups.append({
                                'type': 'modal',
                                'selector': selector,
                                'action': 'closed'
                            })
                            return result
                except Exception:
                    continue

            return None

        except Exception as e:
            self.logger.error(f"Error handling modal: {e}")
            return None

    async def _close_modal(self, page: Page, modal) -> Optional[Dict[str, Any]]:
        """
        Try to close a modal dialog.

        Args:
            page: Playwright page instance
            modal: Modal element

        Returns:
            Dictionary with close action info if successful, None otherwise
        """
        # Try various close button selectors
        close_selectors = [
            'button[aria-label*="close"]',
            'button[aria-label*="Close"]',
            'button.close',
            '[class*="close-button"]',
            '[class*="modal-close"]',
            'button:has-text("×")',
            'button:has-text("Close")',
            'button:has-text("OK")',
            'button:has-text("Got it")'
        ]

        for selector in close_selectors:
            try:
                button = await page.query_selector(selector)
                if button and await button.is_visible():
                    text = await button.text_content()
                    # Check if safe to click
                    if text and not self._contains_unsafe_keyword(text):
                        await button.click()
                        await page.wait_for_timeout(500)
                        return {
                            'selector': selector,
                            'button_text': text
                        }
            except Exception:
                continue

        return None

    def _contains_unsafe_keyword(self, text: str) -> bool:
        """
        Check if text contains unsafe keywords.

        Args:
            text: Text to check

        Returns:
            True if contains unsafe keyword, False otherwise
        """
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in self.UNSAFE_KEYWORDS)

    async def handle_all_popups(self, page: Page) -> int:
        """
        Attempt to handle all types of popups on the current page.

        Args:
            page: Playwright page instance

        Returns:
            Number of popups handled
        """
        handled_count = 0

        # Handle cookie consent
        if await self.handle_cookie_consent(page):
            handled_count += 1

        # Handle modals
        modal_result = await self.handle_modal(page)
        if modal_result:
            handled_count += 1

        return handled_count

    def get_handled_popups(self) -> List[Dict[str, Any]]:
        """
        Get list of all handled popups.

        Returns:
            List of popup interaction records
        """
        return self.handled_popups.copy()

    def reset(self):
        """Reset the handler state."""
        self.handled_popups.clear()
