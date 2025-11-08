# Prompt Integration Guide
# How to Use AI Prompts with the Web Exploratory Testing Framework

## Overview

This guide explains how to integrate the AI prompts with your exploratory testing framework to enable true AI-powered decision making using LLM APIs (OpenAI, Anthropic Claude, etc.).

## Prompt Files

### 1. Master Exploration Prompt
**File**: `master_exploration_prompt.md`
**Purpose**: Comprehensive step-by-step guidance for entire exploration process
**When to Use**: System initialization, reference for all decision-making

### 2. Element Selection Prompt
**File**: `element_selection_prompt.md`
**Purpose**: Intelligent element selection and prioritization
**When to Use**: When choosing next action from multiple elements

### 3. Action Validation Prompt
**File**: `action_validation_prompt.md`
**Purpose**: Validate actions for safety and value before execution
**When to Use**: Before executing every action

### 4. Insights Generation Prompt
**File**: `insights_generation_prompt.md`
**Purpose**: Generate insights and recommendations from exploration data
**When to Use**: After exploration completes, for final report

### 5. Configuration File
**File**: `prompt_config.yaml`
**Purpose**: Configuration settings and guardrails

---

## Integration Architecture

```
┌─────────────────────────────────────────────┐
│         Explorer Agent (Current)             │
│    (Heuristic-based decision making)        │
└─────────────────────┬───────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────┐
│      AI-Enhanced Explorer Agent (New)        │
│                                              │
│  ┌────────────────────────────────────┐    │
│  │  1. Load Master Prompt             │    │
│  │  2. Get Available Elements         │    │
│  │  3. Call LLM with Element          │    │
│  │     Selection Prompt               │    │
│  │  4. Validate Action with LLM       │    │
│  │  5. Execute Safe Action            │    │
│  │  6. Generate Insights with LLM     │    │
│  └────────────────────────────────────┘    │
└─────────────────────────────────────────────┘
```

---

## Step-by-Step Integration

### Step 1: Install LLM API Client

Choose your preferred LLM provider:

**Option A: OpenAI**
```bash
pip install openai
```

**Option B: Anthropic Claude**
```bash
pip install anthropic
```

**Option C: Local LLM (Ollama)**
```bash
pip install ollama
```

### Step 2: Set Up API Keys

Create a `.env` file:
```bash
# .env file
OPENAI_API_KEY=your_openai_key_here
ANTHROPIC_API_KEY=your_anthropic_key_here

# Choose provider
LLM_PROVIDER=openai  # or anthropic, or ollama
LLM_MODEL=gpt-4      # or claude-3-sonnet-20240229, or llama2
```

### Step 3: Create LLM Helper Module

Create `core/llm_helper.py`:

```python
"""
LLM Helper for AI-powered decision making.
"""

import os
import json
from typing import Dict, Any, Optional
from pathlib import Path


class LLMHelper:
    """Helper class for LLM API interactions."""

    def __init__(self, provider: str = "openai", model: str = "gpt-4"):
        """
        Initialize LLM helper.

        Args:
            provider: LLM provider (openai, anthropic, ollama)
            model: Model name
        """
        self.provider = provider
        self.model = model
        self.prompts_dir = Path(__file__).parent.parent / "prompts"

        # Initialize API client
        if provider == "openai":
            import openai
            openai.api_key = os.getenv("OPENAI_API_KEY")
            self.client = openai
        elif provider == "anthropic":
            import anthropic
            self.client = anthropic.Anthropic(
                api_key=os.getenv("ANTHROPIC_API_KEY")
            )
        elif provider == "ollama":
            import ollama
            self.client = ollama
        else:
            raise ValueError(f"Unsupported provider: {provider}")

    def load_prompt(self, prompt_file: str) -> str:
        """Load prompt from file."""
        prompt_path = self.prompts_dir / prompt_file
        with open(prompt_path, 'r') as f:
            return f.read()

    async def select_element(
        self,
        current_url: str,
        page_title: str,
        elements: list,
        context: dict
    ) -> Dict[str, Any]:
        """
        Use LLM to select best element for interaction.

        Args:
            current_url: Current page URL
            page_title: Page title
            elements: List of available elements
            context: Exploration context

        Returns:
            Selected element with reasoning
        """
        # Load element selection prompt
        system_prompt = self.load_prompt("element_selection_prompt.md")

        # Build user message with current data
        user_message = f"""
Current URL: {current_url}
Page Title: {page_title}

Available Elements:
{json.dumps(elements, indent=2)}

Exploration Context:
- Previously visited URLs: {len(context.get('visited_urls', []))}
- Current step: {context.get('current_step', 0)}
- Max steps: {context.get('max_steps', 50)}

Select the BEST element for next interaction.
"""

        # Call LLM
        if self.provider == "openai":
            response = await self._call_openai(system_prompt, user_message)
        elif self.provider == "anthropic":
            response = await self._call_anthropic(system_prompt, user_message)
        else:
            response = await self._call_ollama(system_prompt, user_message)

        # Parse JSON response
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            # Fallback to first safe element if JSON parsing fails
            return self._fallback_selection(elements)

    async def validate_action(
        self,
        action: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Use LLM to validate action before execution.

        Args:
            action: Proposed action
            context: Current context

        Returns:
            Validation result with safety/value scores
        """
        system_prompt = self.load_prompt("action_validation_prompt.md")

        user_message = f"""
Proposed Action:
{json.dumps(action, indent=2)}

Current Context:
{json.dumps(context, indent=2)}

Validate this action for safety and testing value.
"""

        if self.provider == "openai":
            response = await self._call_openai(system_prompt, user_message)
        elif self.provider == "anthropic":
            response = await self._call_anthropic(system_prompt, user_message)
        else:
            response = await self._call_ollama(system_prompt, user_message)

        try:
            return json.loads(response)
        except json.JSONDecodeError:
            # Fallback to basic validation
            return self._fallback_validation(action)

    async def generate_insights(
        self,
        session_data: Dict[str, Any]
    ) -> str:
        """
        Generate insights from exploration session.

        Args:
            session_data: Complete session data

        Returns:
            Markdown-formatted insights report
        """
        system_prompt = self.load_prompt("insights_generation_prompt.md")

        user_message = f"""
Session Summary:
{json.dumps(session_data.get('summary', {}), indent=2)}

Interaction History:
{json.dumps(session_data.get('interactions', [])[:10], indent=2)}
... and {len(session_data.get('interactions', [])) - 10} more interactions

Generate comprehensive insights and recommendations.
"""

        if self.provider == "openai":
            response = await self._call_openai(system_prompt, user_message)
        elif self.provider == "anthropic":
            response = await self._call_anthropic(system_prompt, user_message)
        else:
            response = await self._call_ollama(system_prompt, user_message)

        return response

    async def _call_openai(self, system_prompt: str, user_message: str) -> str:
        """Call OpenAI API."""
        response = await self.client.ChatCompletion.acreate(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            temperature=0.3,
            max_tokens=1000
        )
        return response.choices[0].message.content

    async def _call_anthropic(self, system_prompt: str, user_message: str) -> str:
        """Call Anthropic API."""
        message = await self.client.messages.create(
            model=self.model,
            max_tokens=1000,
            temperature=0.3,
            system=system_prompt,
            messages=[
                {"role": "user", "content": user_message}
            ]
        )
        return message.content[0].text

    async def _call_ollama(self, system_prompt: str, user_message: str) -> str:
        """Call Ollama local LLM."""
        response = await self.client.chat(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ]
        )
        return response['message']['content']

    def _fallback_selection(self, elements: list) -> Dict[str, Any]:
        """Fallback element selection if LLM fails."""
        # Simple heuristic fallback
        for element in elements:
            if 'login' in element.get('text', '').lower():
                return {
                    "selected_element": element,
                    "reasoning": "Fallback: Selected login element",
                    "confidence": "medium"
                }
        return {
            "selected_element": elements[0] if elements else None,
            "reasoning": "Fallback: Selected first available element",
            "confidence": "low"
        }

    def _fallback_validation(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback validation if LLM fails."""
        # Basic safety check
        unsafe_keywords = ["delete", "remove", "logout", "purchase"]
        element_text = action.get('element', {}).get('text', '').lower()

        is_safe = not any(keyword in element_text for keyword in unsafe_keywords)

        return {
            "validation_result": "APPROVED" if is_safe else "REJECTED",
            "safety_score": 8 if is_safe else 2,
            "value_score": 6,
            "reasoning": "Fallback safety check"
        }
```

### Step 4: Update Explorer Agent

Modify `agents/explorer_agent.py` to use LLM:

```python
# Add at top of file
from core.llm_helper import LLMHelper
import os

class ExplorerAgent:
    def __init__(self, browser, state_tracker, screenshot_agent, max_steps, logger, use_llm=False):
        # ... existing code ...

        # Initialize LLM helper if enabled
        self.use_llm = use_llm
        if use_llm:
            provider = os.getenv("LLM_PROVIDER", "openai")
            model = os.getenv("LLM_MODEL", "gpt-4")
            self.llm_helper = LLMHelper(provider, model)
            logger.info(f"LLM-powered exploration enabled: {provider}/{model}")

    async def _select_next_action(self, elements):
        """Select next action - enhanced with LLM."""
        if self.use_llm:
            # Use LLM for intelligent selection
            context = {
                'visited_urls': list(self.state_tracker.visited_urls),
                'current_step': self.state_tracker.current_step,
                'max_steps': self.max_steps
            }

            current_url = await self.browser.get_current_url()
            page_title = await self.browser.get_page_title()

            try:
                llm_response = await self.llm_helper.select_element(
                    current_url=current_url,
                    page_title=page_title,
                    elements=elements,
                    context=context
                )

                self.logger.info(f"LLM selected: {llm_response.get('selected_element', {}).get('text')}")
                self.logger.debug(f"LLM reasoning: {llm_response.get('reasoning')}")

                return self._create_action_from_llm_response(llm_response)

            except Exception as e:
                self.logger.warning(f"LLM selection failed, using heuristic: {e}")
                # Fall back to heuristic method
                return await self._select_next_action_heuristic(elements)
        else:
            # Use existing heuristic method
            return await self._select_next_action_heuristic(elements)

    async def _validate_action(self, action):
        """Validate action before execution - enhanced with LLM."""
        if self.use_llm:
            context = {
                'current_url': await self.browser.get_current_url(),
                'current_step': self.state_tracker.current_step,
                'max_steps': self.max_steps
            }

            try:
                validation = await self.llm_helper.validate_action(action, context)

                if validation['validation_result'] == 'REJECTED':
                    self.logger.warning(f"Action rejected by LLM: {validation['reasoning']}")
                    return False

                if validation['validation_result'] == 'MODIFIED':
                    self.logger.info(f"Action needs modification: {validation['modifications']}")
                    # Apply modifications if possible

                return validation['validation_result'] in ['APPROVED', 'MODIFIED']

            except Exception as e:
                self.logger.warning(f"LLM validation failed, using basic check: {e}")
                return self.action_handler.is_safe_action(action.get('text', ''))
        else:
            # Use existing safety check
            return self.action_handler.is_safe_action(action.get('text', ''))
```

### Step 5: Update Main Entry Point

Modify `main.py` to support LLM mode:

```python
def parse_arguments():
    parser = argparse.ArgumentParser(...)

    # ... existing arguments ...

    parser.add_argument(
        '--use-llm',
        action='store_true',
        help='Enable LLM-powered decision making (requires API key)'
    )

    parser.add_argument(
        '--llm-provider',
        type=str,
        default='openai',
        choices=['openai', 'anthropic', 'ollama'],
        help='LLM provider to use'
    )

    parser.add_argument(
        '--llm-model',
        type=str,
        default='gpt-4',
        help='LLM model name'
    )

    return parser.parse_args()

async def main():
    args = parse_arguments()

    # Set environment variables for LLM
    if args.use_llm:
        os.environ['LLM_PROVIDER'] = args.llm_provider
        os.environ['LLM_MODEL'] = args.llm_model

    # Create tester with LLM option
    tester = WebExploratoryTester(
        url=args.url,
        max_steps=args.max_steps,
        depth=args.depth,
        headless=args.headless,
        use_llm=args.use_llm
    )

    await tester.run()
```

### Step 6: Generate LLM-Powered Insights

Update `report_agent.py` to use LLM for insights:

```python
from core.llm_helper import LLMHelper

class ReportAgent:
    def __init__(self, output_dir, logger, use_llm=False):
        # ... existing code ...
        self.use_llm = use_llm
        if use_llm:
            self.llm_helper = LLMHelper()

    async def generate_insights(self, state_tracker):
        """Generate insights using LLM."""
        if self.use_llm:
            try:
                session_data = {
                    'summary': state_tracker.get_summary(),
                    'interactions': [r.to_dict() for r in state_tracker.interaction_history]
                }

                insights = await self.llm_helper.generate_insights(session_data)
                return insights

            except Exception as e:
                self.logger.error(f"LLM insights generation failed: {e}")
                return self._generate_basic_insights(state_tracker)
        else:
            return self._generate_basic_insights(state_tracker)
```

---

## Usage Examples

### Example 1: Run with OpenAI GPT-4

```bash
# Set API key
export OPENAI_API_KEY=your_key_here

# Run with LLM
python main.py \
    --url https://example.com \
    --use-llm \
    --llm-provider openai \
    --llm-model gpt-4 \
    --max-steps 50
```

### Example 2: Run with Anthropic Claude

```bash
# Set API key
export ANTHROPIC_API_KEY=your_key_here

# Run with Claude
python main.py \
    --url https://example.com \
    --use-llm \
    --llm-provider anthropic \
    --llm-model claude-3-sonnet-20240229 \
    --max-steps 50
```

### Example 3: Run with Local LLM (Ollama)

```bash
# Start Ollama server first
ollama serve

# Pull model
ollama pull llama2

# Run with local LLM
python main.py \
    --url https://example.com \
    --use-llm \
    --llm-provider ollama \
    --llm-model llama2 \
    --max-steps 50
```

### Example 4: Programmatic Usage

```python
from main import WebExploratoryTester
import os

# Set API key
os.environ['OPENAI_API_KEY'] = 'your_key_here'

# Create tester with LLM
tester = WebExploratoryTester(
    url="https://example.com",
    max_steps=50,
    use_llm=True,
    llm_provider="openai",
    llm_model="gpt-4"
)

# Run exploration
await tester.run()
```

---

## Benefits of LLM Integration

### 1. Intelligent Element Selection
- **Without LLM**: Fixed priority scoring based on keywords
- **With LLM**: Context-aware reasoning about element purpose and testing value

### 2. Adaptive Safety Validation
- **Without LLM**: Keyword-based safety checks
- **With LLM**: Semantic understanding of action implications

### 3. Comprehensive Insights
- **Without LLM**: Basic statistics and error listing
- **With LLM**: Detailed analysis, pattern recognition, actionable recommendations

### 4. Natural Language Reasoning
- **Without LLM**: No explanation of decisions
- **With LLM**: Clear reasoning for every choice

---

## Cost Considerations

### OpenAI GPT-4
- **Cost**: ~$0.03 per 1K input tokens, ~$0.06 per 1K output tokens
- **Estimated**: $0.50 - $2.00 per 50-step exploration
- **Recommendation**: Use for production testing, important applications

### Anthropic Claude
- **Cost**: ~$0.015 per 1K input tokens, ~$0.075 per 1K output tokens
- **Estimated**: $0.40 - $1.80 per 50-step exploration
- **Recommendation**: Good balance of cost and performance

### Local LLM (Ollama)
- **Cost**: Free (requires local compute)
- **Estimated**: No API costs, uses local GPU/CPU
- **Recommendation**: Use for development, learning, frequent testing

---

## Best Practices

### 1. Start Without LLM
- Test framework with heuristic mode first
- Verify basic functionality works
- Understand baseline behavior

### 2. Enable LLM Gradually
- Start with element selection only
- Add validation once comfortable
- Enable insights generation last

### 3. Monitor API Usage
- Track API calls and costs
- Set rate limits if needed
- Cache responses when possible

### 4. Fallback Strategy
- Always have heuristic fallback
- Handle API failures gracefully
- Log when LLM calls fail

### 5. Validate LLM Responses
- Verify JSON format
- Check for required fields
- Sanitize outputs before use

---

## Troubleshooting

### Issue: API Key Not Found
```
Error: OPENAI_API_KEY not set
```
**Solution**: Set environment variable or create `.env` file

### Issue: JSON Parsing Error
```
Error: JSON decode error from LLM response
```
**Solution**: LLM returned invalid JSON, fallback will activate automatically

### Issue: Rate Limit Exceeded
```
Error: Rate limit exceeded
```
**Solution**: Add delays between calls, reduce frequency, or upgrade API tier

### Issue: High API Costs
**Solution**:
- Use cheaper models (gpt-3.5-turbo instead of gpt-4)
- Reduce max_steps
- Use LLM selectively (only for complex decisions)

---

## Conclusion

With these prompts and integration guide, your framework now has comprehensive AI guidance for:

1. **Step-by-step exploration** (Master Prompt)
2. **Intelligent element selection** (Selection Prompt)
3. **Safety validation** (Validation Prompt)
4. **Insightful reporting** (Insights Prompt)

You can run the framework:
- **Without LLM**: Fast, no API costs, heuristic-based (current implementation)
- **With LLM**: Intelligent, adaptive, context-aware (optional enhancement)

Choose the mode that best fits your needs, budget, and use case!
