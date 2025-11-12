#!/usr/bin/env python3
"""
Example usage of the Web Exploratory Testing Framework.

This script demonstrates different ways to use the framework programmatically.
"""

import asyncio
import sys
from pathlib import Path

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

from main import WebExploratoryTester


async def example_basic_test():
    """Example 1: Basic website exploration."""
    print("=" * 80)
    print("Example 1: Basic Exploration")
    print("=" * 80)

    tester = WebExploratoryTester(
        url="https://example.com",
        max_steps=25,
        depth=2,
        headless=False  # Browser visible by default
    )

    success = await tester.run()
    print(f"\nTest completed: {'SUCCESS' if success else 'FAILED'}")


async def example_extended_test():
    """Example 2: Extended exploration with more steps."""
    print("\n" + "=" * 80)
    print("Example 2: Extended Exploration")
    print("=" * 80)

    tester = WebExploratoryTester(
        url="https://demo.testfire.net",
        max_steps=100,
        depth=5,
        headless=False,  # Browser visible by default
        output_base="outputs/demo_testfire"
    )

    success = await tester.run()
    print(f"\nTest completed: {'SUCCESS' if success else 'FAILED'}")


async def example_visible_browser():
    """Example 3: Run with visible browser (for debugging)."""
    print("\n" + "=" * 80)
    print("Example 3: Visible Browser Mode")
    print("=" * 80)

    tester = WebExploratoryTester(
        url="https://example.com",
        max_steps=10,
        depth=2,
        headless=False,  # Browser will be visible
    )

    success = await tester.run()
    print(f"\nTest completed: {'SUCCESS' if success else 'FAILED'}")


async def run_all_examples():
    """Run all examples sequentially."""
    print("\n🚀 Running All Examples\n")

    # Example 1: Basic test
    await example_basic_test()

    # Wait a bit between examples
    await asyncio.sleep(2)

    # Example 2: Extended test (commented out by default as it takes longer)
    # await example_extended_test()

    # Example 3: Visible browser (commented out to not pop up windows)
    # await example_visible_browser()

    print("\n" + "=" * 80)
    print("✓ All examples completed!")
    print("=" * 80)


if __name__ == "__main__":
    print("""
    Web Exploratory Testing Framework - Examples

    This script demonstrates different usage patterns.
    Edit the script to uncomment different examples.

    Available examples:
    1. example_basic_test() - Quick exploration
    2. example_extended_test() - Thorough exploration
    3. example_visible_browser() - Watch the browser in action
    """)

    # Run all examples
    asyncio.run(run_all_examples())
