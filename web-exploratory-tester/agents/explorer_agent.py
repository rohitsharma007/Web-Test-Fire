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
        logger: Optional[logging.Logger] = None,
        username: Optional[str] = None,
        password: Optional[str] = None
    ):
        """
        Initialize explorer agent.

        Args:
            browser: Browser manager instance
            state_tracker: State tracker instance
            screenshot_agent: Screenshot agent instance
            max_steps: Maximum exploration steps
            logger: Logger instance
            username: Username for login (if authentication is required)
            password: Password for login (if authentication is required)
        """
        self.browser = browser
        self.state_tracker = state_tracker
        self.screenshot_agent = screenshot_agent
        self.max_steps = max_steps
        self.logger = logger or logging.getLogger(__name__)
        self.username = username
        self.password = password

        self.action_handler = ActionHandler(browser, logger)
        self.exploration_complete = False
        self.login_attempted = False
        self.login_successful = False

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

            # Check if credentials are provided and page needs login
            if self.username and self.password and not self.login_attempted:
                is_login_page = await self._is_login_page()
                if is_login_page:
                    self.logger.info("Login page detected - attempting automatic login")
                    login_success = await self._perform_login()
                    if login_success:
                        self.logger.info("Login successful! Continuing exploration...")
                        self.login_successful = True
                    else:
                        self.logger.warning("Login failed - continuing exploration anyway")

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

    async def _is_login_page(self) -> bool:
        """
        Detect if the current page is a login page.

        Returns:
            True if login page detected, False otherwise
        """
        try:
            # Get all visible elements
            elements = await self.browser.get_visible_elements()

            # Look for login indicators
            login_indicators = [
                'username', 'user name', 'email', 'login', 'sign in',
                'password', 'passwd', 'pwd'
            ]

            # Check page title and URL
            page_title = await self.browser.get_page_title()
            current_url = await self.browser.get_current_url()

            title_lower = page_title.lower()
            url_lower = current_url.lower()

            # Check if URL or title contains login indicators
            if any(indicator in url_lower or indicator in title_lower
                   for indicator in ['login', 'signin', 'auth']):
                self.logger.debug("Login page detected from URL/title")
                return True

            # Check for password input fields
            password_fields = [el for el in elements
                             if el.get('type') == 'password' or
                             'password' in el.get('text', '').lower()]

            # Check for username/email input fields
            username_fields = [el for el in elements
                             if any(indicator in el.get('text', '').lower()
                                  for indicator in login_indicators)]

            # If we have both password and username fields, it's likely a login page
            if password_fields and username_fields:
                self.logger.debug(f"Login page detected: found {len(password_fields)} password field(s) and {len(username_fields)} username field(s)")
                return True

            return False

        except Exception as e:
            self.logger.error(f"Error detecting login page: {e}")
            return False

    async def _perform_login(self) -> bool:
        """
        Perform intelligent automatic login with multiple retry strategies.

        Returns:
            True if login successful, False otherwise
        """
        self.login_attempted = True
        max_login_attempts = 3  # Try up to 3 times with different strategies

        for attempt in range(1, max_login_attempts + 1):
            try:
                self.logger.info(f"Login attempt {attempt}/{max_login_attempts} with username: {self.username}")

                # Strategy: Use JavaScript to find fields more reliably
                login_result = await self._attempt_login_with_js_strategy(attempt)

                if login_result:
                    self.login_successful = True
                    return True

                # If first attempt failed, wait and retry with different approach
                if attempt < max_login_attempts:
                    self.logger.warning(f"Login attempt {attempt} failed - retrying with different strategy...")
                    await self.browser.page.wait_for_timeout(2000)

                    # Try to reload the login page for fresh attempt
                    try:
                        current_url = await self.browser.get_current_url()
                        await self.browser.navigate(current_url)
                    except:
                        pass

            except Exception as e:
                self.logger.error(f"Login attempt {attempt} failed with error: {e}")
                if attempt < max_login_attempts:
                    await self.browser.page.wait_for_timeout(2000)
                continue

        self.logger.error(f"All {max_login_attempts} login attempts failed")
        return False

    async def _attempt_login_with_js_strategy(self, attempt: int) -> bool:
        """
        Attempt login using JavaScript-based field detection with multiple strategies.

        Args:
            attempt: Attempt number (1, 2, or 3) to use different strategies

        Returns:
            True if login successful, False otherwise
        """
        try:
            # Wait for page to be ready
            await self.browser.page.wait_for_timeout(1500)

            # Strategy 1: Direct JavaScript selector approach (most reliable)
            if attempt == 1:
                self.logger.info("Strategy 1: Using JavaScript to find fields by attributes")
                username_selector = await self._find_username_field_js()
                password_selector = await self._find_password_field_js()
            # Strategy 2: Try by placeholder and label text
            elif attempt == 2:
                self.logger.info("Strategy 2: Using placeholder and label matching")
                username_selector = await self._find_field_by_placeholder_or_label('username')
                password_selector = await self._find_field_by_placeholder_or_label('password')
            # Strategy 3: Try by index (first text input, first password input)
            else:
                self.logger.info("Strategy 3: Using field index (first text/password inputs)")
                username_selector = await self._find_first_input_by_type('text')
                password_selector = await self._find_first_input_by_type('password')

            if not username_selector:
                self.logger.error(f"Username field not found (Strategy {attempt})")
                return False

            if not password_selector:
                self.logger.error(f"Password field not found (Strategy {attempt})")
                return False

            self.logger.info(f"Found login fields with Strategy {attempt} - filling credentials...")
            self.logger.debug(f"Username selector: {username_selector}")
            self.logger.debug(f"Password selector: {password_selector}")

            # Clear fields first
            await self._clear_and_fill_field(username_selector, self.username)
            self.logger.info("✓ Username entered successfully")
            await self.browser.page.wait_for_timeout(800)

            await self._clear_and_fill_field(password_selector, self.password)
            self.logger.info("✓ Password entered successfully")
            await self.browser.page.wait_for_timeout(800)

            # Find and click submit button using multiple strategies
            submit_clicked = await self._find_and_click_submit_button(attempt)

            if not submit_clicked:
                self.logger.warning("Submit button not found - pressing Enter key")
                await self.browser.page.keyboard.press('Enter')

            # Wait for navigation or page change
            self.logger.info("Waiting for login to process...")
            await self.browser.page.wait_for_timeout(3000)

            # Verify login success
            is_still_login = await self._is_login_page()

            if not is_still_login:
                current_url = await self.browser.get_current_url()
                self.logger.info(f"✓ Login successful! Now at: {current_url}")

                # Capture screenshot after successful login
                await self.screenshot_agent.capture(
                    self.browser,
                    step=1,
                    action_description="successful_login",
                    timestamp=get_iso_timestamp()
                )

                # Record login interaction
                self.state_tracker.record_interaction(
                    action_type='login',
                    element_selector='login_form',
                    element_text=f'Logged in as {self.username}',
                    url_before=current_url,
                    url_after=await self.browser.get_current_url(),
                    screenshot_path=None,
                    notes=f"Automatic login successful (Strategy {attempt})",
                    success=True
                )

                return True
            else:
                self.logger.warning(f"Still on login page after submission (Strategy {attempt})")
                return False

        except Exception as e:
            self.logger.error(f"Login strategy {attempt} failed: {e}")
            return False

    async def _find_username_field_js(self) -> Optional[str]:
        """Find username field using JavaScript with multiple selectors."""
        try:
            selector = await self.browser.page.evaluate("""
                () => {
                    // Try multiple strategies to find username field
                    let field = null;

                    // Strategy 1: By name attribute
                    field = document.querySelector('input[name*="username" i]') ||
                            document.querySelector('input[name*="user" i]') ||
                            document.querySelector('input[name*="email" i]') ||
                            document.querySelector('input[name*="login" i]');
                    if (field) return `input[name="${field.name}"]`;

                    // Strategy 2: By id attribute
                    field = document.querySelector('input[id*="username" i]') ||
                            document.querySelector('input[id*="user" i]') ||
                            document.querySelector('input[id*="email" i]') ||
                            document.querySelector('input[id*="login" i]');
                    if (field) return `input[id="${field.id}"]`;

                    // Strategy 3: By placeholder
                    field = document.querySelector('input[placeholder*="username" i]') ||
                            document.querySelector('input[placeholder*="user" i]') ||
                            document.querySelector('input[placeholder*="email" i]');
                    if (field) return `input[placeholder*="${field.placeholder}"]`;

                    // Strategy 4: By autocomplete attribute
                    field = document.querySelector('input[autocomplete="username"]') ||
                            document.querySelector('input[autocomplete="email"]');
                    if (field) return `input[autocomplete="${field.autocomplete}"]`;

                    // Strategy 5: First text input before password field
                    const passwordField = document.querySelector('input[type="password"]');
                    if (passwordField) {
                        const allInputs = Array.from(document.querySelectorAll('input[type="text"], input[type="email"], input:not([type])'));
                        for (let input of allInputs) {
                            if (input.compareDocumentPosition(passwordField) & Node.DOCUMENT_POSITION_FOLLOWING) {
                                if (input.id) return `input[id="${input.id}"]`;
                                if (input.name) return `input[name="${input.name}"]`;
                                return `input[type="${input.type || 'text'}"]`;
                            }
                        }
                    }

                    return null;
                }
            """)
            return selector
        except Exception as e:
            self.logger.debug(f"JS username field search failed: {e}")
            return None

    async def _find_password_field_js(self) -> Optional[str]:
        """Find password field using JavaScript."""
        try:
            selector = await self.browser.page.evaluate("""
                () => {
                    const field = document.querySelector('input[type="password"]');
                    if (!field) return null;

                    // Try to create most specific selector
                    if (field.name) return `input[name="${field.name}"]`;
                    if (field.id) return `input[id="${field.id}"]`;
                    return 'input[type="password"]';
                }
            """)
            return selector
        except Exception as e:
            self.logger.debug(f"JS password field search failed: {e}")
            return None

    async def _find_field_by_placeholder_or_label(self, field_type: str) -> Optional[str]:
        """Find field by matching placeholder or associated label text."""
        try:
            if field_type == 'username':
                keywords = ['username', 'user', 'email', 'login']
            else:
                keywords = ['password', 'pass']

            elements = await self.browser.get_visible_elements()

            for el in elements:
                if el.get('tag') != 'input':
                    continue

                # Check placeholder, id, name
                text = el.get('text', '').lower()
                el_id = el.get('id', '').lower()

                for keyword in keywords:
                    if keyword in text or keyword in el_id:
                        if field_type == 'password' and el.get('type') == 'password':
                            return el['selector']
                        elif field_type == 'username' and el.get('type') in ['text', 'email', '']:
                            return el['selector']

            return None
        except Exception as e:
            self.logger.debug(f"Placeholder/label search failed: {e}")
            return None

    async def _find_first_input_by_type(self, input_type: str) -> Optional[str]:
        """Find first input of specified type (fallback strategy)."""
        try:
            if input_type == 'text':
                selector = await self.browser.page.evaluate("""
                    () => {
                        const field = document.querySelector('input[type="text"], input[type="email"], input:not([type="password"]):not([type="hidden"])');
                        if (!field) return null;
                        if (field.name) return `input[name="${field.name}"]`;
                        if (field.id) return `input[id="${field.id}"]`;
                        return 'input[type="text"]';
                    }
                """)
            else:  # password
                selector = 'input[type="password"]'

            return selector
        except Exception as e:
            self.logger.debug(f"Input type search failed: {e}")
            return None

    async def _clear_and_fill_field(self, selector: str, value: str):
        """Clear field and fill with value using multiple methods for reliability."""
        try:
            # Wait for field to be visible
            await self.browser.page.wait_for_selector(selector, state='visible', timeout=5000)

            # Click to focus
            await self.browser.page.click(selector)
            await self.browser.page.wait_for_timeout(300)

            # Clear existing content (multiple methods for reliability)
            await self.browser.page.fill(selector, '')
            await self.browser.page.evaluate(f'document.querySelector("{selector}").value = ""')

            # Type the value
            await self.browser.page.type(selector, value, delay=50)
            await self.browser.page.wait_for_timeout(300)

            # Verify the value was entered
            entered_value = await self.browser.page.evaluate(f'document.querySelector("{selector}").value')
            if entered_value != value:
                self.logger.warning(f"Field value mismatch - retrying. Expected: {value}, Got: {entered_value}")
                await self.browser.page.fill(selector, value)

        except Exception as e:
            self.logger.error(f"Failed to fill field {selector}: {e}")
            raise

    async def _find_and_click_submit_button(self, attempt: int) -> bool:
        """Find and click login submit button using multiple strategies."""
        try:
            # Strategy 1: JavaScript-based button detection
            if attempt == 1:
                button_selector = await self.browser.page.evaluate("""
                    () => {
                        const buttons = Array.from(document.querySelectorAll('button, input[type="submit"], a[role="button"]'));
                        for (let btn of buttons) {
                            const text = (btn.textContent || btn.value || '').toLowerCase();
                            if (text.includes('login') || text.includes('sign in') || text.includes('submit')) {
                                if (btn.id) return `#${btn.id}`;
                                if (btn.name) return `[name="${btn.name}"]`;
                                return `button:has-text("${btn.textContent}")`;
                            }
                        }
                        return null;
                    }
                """)

                if button_selector:
                    await self.browser.page.click(button_selector)
                    self.logger.info(f"✓ Clicked submit button: {button_selector}")
                    return True

            # Strategy 2: Using visible elements
            elements = await self.browser.get_visible_elements()
            for el in elements:
                text_lower = el.get('text', '').lower()
                tag = el.get('tag', '').lower()
                el_type = el.get('type', '').lower()

                if (tag == 'button' or el_type == 'submit') and \
                   any(kw in text_lower for kw in ['login', 'sign in', 'submit', 'log in']):
                    await self.browser.click_element(el['selector'])
                    self.logger.info(f"✓ Clicked submit button: {el['text']}")
                    return True

            return False

        except Exception as e:
            self.logger.debug(f"Submit button click failed: {e}")
            return False

    def get_summary(self) -> Dict[str, Any]:
        """
        Get exploration summary.

        Returns:
            Summary dictionary
        """
        summary = self.state_tracker.get_summary()
        # Add login status to summary
        summary['login_attempted'] = self.login_attempted
        summary['login_successful'] = self.login_successful
        return summary
