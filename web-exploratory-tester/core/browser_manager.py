"""
Browser management module for the web exploratory testing framework.
Handles browser lifecycle, navigation, and basic interactions using Playwright.
"""

import asyncio
import logging
from typing import Optional, List, Dict, Any
from playwright.async_api import async_playwright, Browser, BrowserContext, Page, ElementHandle
from .popup_handler import PopupHandler


class BrowserManager:
    """
    Manages browser lifecycle and provides utility functions for web interaction.
    """

    def __init__(
        self,
        headless: bool = True,
        viewport_width: int = 1920,
        viewport_height: int = 1080,
        logger: Optional[logging.Logger] = None
    ):
        """
        Initialize browser manager.

        Args:
            headless: Run browser in headless mode
            viewport_width: Browser viewport width
            viewport_height: Browser viewport height
            logger: Logger instance
        """
        self.headless = headless
        self.viewport_width = viewport_width
        self.viewport_height = viewport_height
        self.logger = logger or logging.getLogger(__name__)

        self.playwright = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        self.popup_handler: Optional[PopupHandler] = None

    async def start(self):
        """Start the browser and create a new page."""
        try:
            self.logger.info("Starting browser...")
            self.playwright = await async_playwright().start()

            # Launch browser with enhanced options for stability
            launch_args = [
                '--disable-blink-features=AutomationControlled',
                '--disable-dev-shm-usage',  # Overcome limited resource problems
                '--disable-gpu',  # Disable GPU hardware acceleration
                '--no-first-run',
                '--no-default-browser-check',
            ]

            self.browser = await self.playwright.chromium.launch(
                headless=self.headless,
                args=launch_args,
                timeout=60000  # Increase launch timeout
            )

            # Verify browser is connected
            if not self.browser.is_connected():
                raise RuntimeError("Browser launched but not connected")

            # Create context with viewport
            self.context = await self.browser.new_context(
                viewport={
                    'width': self.viewport_width,
                    'height': self.viewport_height
                },
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
                ignore_https_errors=True  # Ignore HTTPS errors
            )

            # Create page
            self.page = await self.context.new_page()

            # Set up page close listener for debugging
            self.page.on("close", lambda: self.logger.warning("Page was closed unexpectedly"))

            # Set up popup handler
            self.popup_handler = PopupHandler(self.logger)
            await self.popup_handler.setup_dialog_handler(self.page)

            # Give browser time to fully initialize
            await asyncio.sleep(1.0)  # Increased from 0.5s to 1.0s

            # Verify page is still open after initialization
            if self.page.is_closed():
                raise RuntimeError("Page closed during initialization")

            # Verify browser is still connected
            if not self.browser.is_connected():
                raise RuntimeError("Browser disconnected during initialization")

            self.logger.info("Browser started successfully")

        except Exception as e:
            self.logger.error(f"Failed to start browser: {e}")
            # Clean up on failure
            await self._cleanup_on_error()
            raise

    async def _cleanup_on_error(self):
        """Clean up resources after an error."""
        try:
            if self.page and not self.page.is_closed():
                await self.page.close()
        except:
            pass
        try:
            if self.context:
                await self.context.close()
        except:
            pass
        try:
            if self.browser:
                await self.browser.close()
        except:
            pass
        try:
            if self.playwright:
                await self.playwright.stop()
        except:
            pass

    async def navigate(self, url: str, timeout: int = 30000) -> bool:
        """
        Navigate to a URL.

        Args:
            url: URL to navigate to
            timeout: Navigation timeout in milliseconds

        Returns:
            True if successful, False otherwise
        """
        if not self.page:
            raise RuntimeError("Browser not started. Call start() first.")

        try:
            # Comprehensive pre-navigation validation
            if not self.browser or not self.browser.is_connected():
                self.logger.error("Browser is not connected")
                return False

            if self.page.is_closed():
                self.logger.error("Page was closed before navigation")
                return False

            if not self.context:
                self.logger.error("Browser context is None")
                return False

            self.logger.info(f"Navigating to: {url}")

            # Navigate with retry logic
            max_retries = 3  # Increased from 2 to 3
            for attempt in range(max_retries):
                try:
                    # Double-check page is still open before each attempt
                    if self.page.is_closed():
                        self.logger.error(f"Page closed before attempt {attempt + 1}")
                        return False

                    # Perform navigation with multiple wait strategies
                    response = await self.page.goto(
                        url,
                        timeout=timeout,
                        wait_until='domcontentloaded'
                    )

                    # Check if navigation was successful
                    if response:
                        self.logger.debug(f"Navigation response status: {response.status}")

                    break

                except Exception as nav_error:
                    error_msg = str(nav_error)
                    self.logger.warning(f"Navigation attempt {attempt + 1}/{max_retries} failed: {error_msg}")

                    # Check if it's a fatal error (browser closed)
                    if "closed" in error_msg.lower():
                        self.logger.error("Browser/page closed during navigation - fatal error")
                        return False

                    if attempt < max_retries - 1:
                        # Wait before retry with exponential backoff
                        wait_time = (attempt + 1) * 1.5
                        self.logger.info(f"Waiting {wait_time}s before retry...")
                        await asyncio.sleep(wait_time)

                        # Verify browser is still alive before retrying
                        if not self.browser.is_connected() or self.page.is_closed():
                            self.logger.error("Browser/page no longer available for retry")
                            return False
                    else:
                        raise nav_error

            # Wait for page to stabilize with shorter timeout
            try:
                await self.page.wait_for_load_state('domcontentloaded', timeout=5000)
            except Exception as e:
                self.logger.debug(f"DOM content load timeout: {e}")

            try:
                await self.page.wait_for_load_state('networkidle', timeout=5000)
            except Exception:
                # Network idle timeout is not critical, continue anyway
                self.logger.debug("Network idle timeout, continuing...")

            # Handle any popups that appear
            if self.popup_handler:
                await self.popup_handler.handle_all_popups(self.page)

            self.logger.info(f"Successfully navigated to: {url}")
            return True

        except Exception as e:
            self.logger.error(f"Navigation failed: {e}")

            # Log browser state for debugging
            try:
                if self.browser:
                    self.logger.error(f"Browser connected: {self.browser.is_connected()}")
                if self.page:
                    self.logger.error(f"Page closed: {self.page.is_closed()}")
            except:
                pass

            return False

    async def get_current_url(self) -> str:
        """Get current page URL."""
        if not self.page:
            return ""
        return self.page.url

    async def get_page_title(self) -> str:
        """Get current page title."""
        if not self.page:
            return ""
        return await self.page.title()

    async def click_element(self, selector: str, timeout: int = 5000) -> bool:
        """
        Click an element by selector.

        Args:
            selector: CSS selector or text selector
            timeout: Timeout in milliseconds

        Returns:
            True if successful, False otherwise
        """
        if not self.page:
            return False

        try:
            await self.page.click(selector, timeout=timeout)
            # Wait for any navigation or dynamic content
            await self.page.wait_for_timeout(1000)
            return True
        except Exception as e:
            self.logger.debug(f"Click failed for {selector}: {e}")
            return False

    async def type_text(self, selector: str, text: str, timeout: int = 5000) -> bool:
        """
        Type text into an input element.

        Args:
            selector: CSS selector
            text: Text to type
            timeout: Timeout in milliseconds

        Returns:
            True if successful, False otherwise
        """
        if not self.page:
            return False

        try:
            await self.page.fill(selector, text, timeout=timeout)
            await self.page.wait_for_timeout(500)
            return True
        except Exception as e:
            self.logger.debug(f"Type text failed for {selector}: {e}")
            return False

    async def select_option(self, selector: str, value: str, timeout: int = 5000) -> bool:
        """
        Select an option from a dropdown.

        Args:
            selector: CSS selector for select element
            value: Option value to select
            timeout: Timeout in milliseconds

        Returns:
            True if successful, False otherwise
        """
        if not self.page:
            return False

        try:
            await self.page.select_option(selector, value, timeout=timeout)
            await self.page.wait_for_timeout(500)
            return True
        except Exception as e:
            self.logger.debug(f"Select option failed for {selector}: {e}")
            return False

    async def scroll_page(self, direction: str = 'down', pixels: int = 500) -> bool:
        """
        Scroll the page.

        Args:
            direction: 'down' or 'up'
            pixels: Number of pixels to scroll

        Returns:
            True if successful, False otherwise
        """
        if not self.page:
            return False

        try:
            scroll_amount = pixels if direction == 'down' else -pixels
            await self.page.evaluate(f"window.scrollBy(0, {scroll_amount})")
            await self.page.wait_for_timeout(500)
            return True
        except Exception as e:
            self.logger.debug(f"Scroll failed: {e}")
            return False

    async def get_visible_elements(self) -> List[Dict[str, Any]]:
        """
        Get all visible interactive elements on the page.

        Returns:
            List of element information dictionaries
        """
        if not self.page:
            return []

        try:
            # Check if page/browser is still alive
            if self.page.is_closed():
                self.logger.warning("Page is closed, cannot get elements")
                return []

            if not self.browser or not self.browser.is_connected():
                self.logger.warning("Browser is disconnected, cannot get elements")
                return []

            # JavaScript to extract visible interactive elements
            elements = await self.page.evaluate("""
                () => {
                    const elements = [];
                    const selectors = [
                        'a[href]',
                        'button',
                        'input[type="text"]',
                        'input[type="email"]',
                        'input[type="search"]',
                        'input[type="submit"]',
                        'select',
                        '[role="button"]',
                        '[onclick]'
                    ];

                    selectors.forEach(selector => {
                        document.querySelectorAll(selector).forEach((el, index) => {
                            const rect = el.getBoundingClientRect();
                            const isVisible = rect.width > 0 && rect.height > 0 &&
                                            rect.top >= 0 && rect.top < window.innerHeight;

                            if (isVisible) {
                                const text = el.innerText || el.textContent || el.value || el.placeholder || '';
                                const tag = el.tagName.toLowerCase();
                                const type = el.type || '';
                                const href = el.href || '';
                                const id = el.id || '';
                                const classes = el.className || '';

                                // Generate a selector
                                let elementSelector = tag;
                                if (id) elementSelector = `#${id}`;
                                else if (text && text.trim()) elementSelector = `${tag}:has-text("${text.trim().slice(0, 30)}")`;
                                else if (classes) elementSelector = `.${classes.split(' ')[0]}`;

                                elements.push({
                                    tag: tag,
                                    type: type,
                                    text: text.trim().slice(0, 100),
                                    href: href,
                                    selector: elementSelector,
                                    id: id,
                                    classes: classes,
                                    position: { x: rect.x, y: rect.y }
                                });
                            }
                        });
                    });

                    return elements;
                }
            """)

            return elements

        except Exception as e:
            error_msg = str(e)
            if "crashed" in error_msg.lower() or "closed" in error_msg.lower():
                self.logger.error(f"Browser/page crashed or closed: {e}")
            else:
                self.logger.error(f"Failed to get visible elements: {e}")
            return []

    async def take_screenshot(self, filepath: str, full_page: bool = False) -> bool:
        """
        Take a screenshot.

        Args:
            filepath: Path to save screenshot
            full_page: Capture full page or just viewport

        Returns:
            True if successful, False otherwise
        """
        if not self.page:
            return False

        try:
            # Check if page/browser is still alive before screenshot
            if self.page.is_closed():
                self.logger.warning("Page is closed, cannot take screenshot")
                return False

            if not self.browser or not self.browser.is_connected():
                self.logger.warning("Browser is disconnected, cannot take screenshot")
                return False

            await self.page.screenshot(path=filepath, full_page=full_page)
            return True
        except Exception as e:
            error_msg = str(e)
            if "crashed" in error_msg.lower() or "closed" in error_msg.lower():
                self.logger.error(f"Browser/page crashed or closed during screenshot: {e}")
            else:
                self.logger.error(f"Screenshot failed: {e}")
            return False

    async def wait_for_navigation(self, timeout: int = 10000):
        """
        Wait for navigation to complete.

        Args:
            timeout: Timeout in milliseconds
        """
        if not self.page:
            return

        try:
            await self.page.wait_for_load_state('networkidle', timeout=timeout)
        except Exception as e:
            self.logger.debug(f"Wait for navigation timeout: {e}")

    async def go_back(self) -> bool:
        """
        Navigate back in browser history.

        Returns:
            True if successful, False otherwise
        """
        if not self.page:
            return False

        try:
            await self.page.go_back(wait_until='domcontentloaded')
            await self.page.wait_for_timeout(1000)
            return True
        except Exception as e:
            self.logger.debug(f"Go back failed: {e}")
            return False

    async def close(self):
        """Close browser and cleanup resources."""
        try:
            if self.page and not self.page.is_closed():
                try:
                    await self.page.close()
                except Exception as e:
                    self.logger.debug(f"Page close error (may already be closed): {e}")

            if self.context:
                try:
                    await self.context.close()
                except Exception as e:
                    self.logger.debug(f"Context close error (may already be closed): {e}")

            if self.browser and self.browser.is_connected():
                try:
                    await self.browser.close()
                except Exception as e:
                    self.logger.debug(f"Browser close error (may already be closed): {e}")

            if self.playwright:
                try:
                    await self.playwright.stop()
                except Exception as e:
                    self.logger.debug(f"Playwright stop error: {e}")

            self.logger.info("Browser closed successfully")

        except Exception as e:
            self.logger.error(f"Error closing browser: {e}")

    async def __aenter__(self):
        """Async context manager entry."""
        await self.start()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()
