"""
Report generation agent for the web exploratory testing framework.
Compiles exploration data into a professional PDF report with screenshots.
"""

import os
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime
from fpdf import FPDF
from core.state_tracker import StateTracker, InteractionRecord
from agents.screenshot_agent import ScreenshotAgent
from core.utils import format_duration, ensure_directory, get_timestamp


class PDF(FPDF):
    """Custom PDF class with header and footer."""

    def __init__(self, title: str = "Web Exploratory Testing Report"):
        super().__init__()
        self.report_title = title

    def header(self):
        """Add header to each page."""
        if self.page_no() > 1:  # Skip header on first page
            self.set_font('Arial', 'B', 10)
            self.cell(0, 10, self.report_title, 0, 1, 'C')
            self.ln(5)

    def footer(self):
        """Add footer to each page."""
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

    def chapter_title(self, title: str):
        """Add a chapter title."""
        self.set_font('Arial', 'B', 14)
        self.set_fill_color(66, 135, 245)
        self.set_text_color(255, 255, 255)
        self.cell(0, 10, title, 0, 1, 'L', True)
        self.set_text_color(0, 0, 0)
        self.ln(5)

    def section_title(self, title: str):
        """Add a section title."""
        self.set_font('Arial', 'B', 12)
        self.set_text_color(66, 135, 245)
        self.cell(0, 8, title, 0, 1, 'L')
        self.set_text_color(0, 0, 0)
        self.ln(2)

    def body_text(self, text: str):
        """Add body text."""
        self.set_font('Arial', '', 10)
        self.multi_cell(0, 5, text)
        self.ln(2)

    def key_value(self, key: str, value: str):
        """Add key-value pair."""
        self.set_font('Arial', 'B', 10)
        self.cell(60, 6, key + ':', 0, 0)
        self.set_font('Arial', '', 10)
        self.multi_cell(0, 6, value)


class ReportAgent:
    """
    Agent responsible for generating comprehensive PDF reports.
    """

    def __init__(
        self,
        output_dir: str = "outputs/reports",
        logger: Optional[logging.Logger] = None
    ):
        """
        Initialize report agent.

        Args:
            output_dir: Directory to save reports
            logger: Logger instance
        """
        self.output_dir = ensure_directory(output_dir)
        self.logger = logger or logging.getLogger(__name__)

    def generate(
        self,
        state_tracker: StateTracker,
        screenshot_agent: ScreenshotAgent,
        report_name: Optional[str] = None
    ) -> Optional[str]:
        """
        Generate comprehensive PDF report.

        Args:
            state_tracker: State tracker with exploration data
            screenshot_agent: Screenshot agent with captured images
            report_name: Custom report name (optional)

        Returns:
            Path to generated report or None if failed
        """
        try:
            self.logger.info("Generating PDF report...")

            # Create PDF
            pdf = PDF()
            pdf.set_auto_page_break(auto=True, margin=15)

            # Add cover page
            self._add_cover_page(pdf, state_tracker)

            # Add summary page
            self._add_summary_page(pdf, state_tracker)

            # Add step-by-step documentation
            self._add_steps_documentation(
                pdf,
                state_tracker.interaction_history,
                screenshot_agent
            )

            # Add observations page
            self._add_observations_page(pdf, state_tracker)

            # Generate filename
            if not report_name:
                timestamp = get_timestamp()
                domain = state_tracker.base_domain.replace('.', '_')
                report_name = f"exploration_report_{domain}_{timestamp}.pdf"

            filepath = os.path.join(self.output_dir, report_name)

            # Save PDF
            pdf.output(filepath)

            self.logger.info(f"Report generated: {filepath}")
            return filepath

        except Exception as e:
            self.logger.error(f"Failed to generate report: {e}")
            return None

    def _add_cover_page(self, pdf: PDF, state_tracker: StateTracker):
        """Add cover page."""
        pdf.add_page()

        # Title
        pdf.set_font('Arial', 'B', 24)
        pdf.ln(60)
        pdf.cell(0, 15, 'Web Exploratory Testing', 0, 1, 'C')
        pdf.cell(0, 15, 'Report', 0, 1, 'C')

        pdf.ln(20)

        # Target URL
        pdf.set_font('Arial', 'B', 14)
        pdf.cell(0, 10, 'Target Website:', 0, 1, 'C')
        pdf.set_font('Arial', '', 12)
        pdf.cell(0, 10, state_tracker.base_url, 0, 1, 'C')

        pdf.ln(10)

        # Date
        pdf.set_font('Arial', '', 11)
        pdf.cell(0, 8, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", 0, 1, 'C')

        pdf.ln(40)

        # Footer info
        pdf.set_font('Arial', 'I', 9)
        pdf.cell(0, 6, 'AI-Driven Exploratory Testing Framework', 0, 1, 'C')
        pdf.cell(0, 6, 'Automated with Intelligent Navigation & Interaction', 0, 1, 'C')

    def _add_summary_page(self, pdf: PDF, state_tracker: StateTracker):
        """Add summary page."""
        pdf.add_page()
        pdf.chapter_title('Exploration Summary')

        summary = state_tracker.get_summary()

        # General info
        pdf.section_title('General Information')
        pdf.key_value('Base URL', summary['base_url'])
        pdf.key_value('Exploration Date', datetime.now().strftime('%Y-%m-%d'))
        pdf.key_value('Duration', format_duration(summary['session_duration_seconds']))
        pdf.ln(5)

        # Statistics
        pdf.section_title('Exploration Statistics')
        pdf.key_value('Total Steps Executed', str(summary['total_steps']))
        pdf.key_value('Unique URLs Visited', str(summary['total_urls_visited']))
        pdf.key_value('Click Actions', str(summary['total_clicks']))
        pdf.key_value('Input Actions', str(summary['total_inputs']))
        pdf.key_value('Navigation Actions', str(summary['total_navigations']))
        pdf.key_value('Popups Handled', str(summary['total_popups_handled']))
        pdf.key_value('Errors Encountered', str(summary['total_errors']))
        pdf.ln(5)

        # Configuration
        pdf.section_title('Configuration')
        pdf.key_value('Maximum Depth', str(summary['max_depth']))
        pdf.key_value('Current Depth Reached', str(summary['current_depth']))

    def _add_steps_documentation(
        self,
        pdf: PDF,
        interactions: List[InteractionRecord],
        screenshot_agent: ScreenshotAgent
    ):
        """Add step-by-step documentation."""
        pdf.add_page()
        pdf.chapter_title('Step-by-Step Documentation')

        for interaction in interactions:
            # Start new page for each step for better layout
            if pdf.get_y() > 200:  # If near bottom of page
                pdf.add_page()

            # Step header
            pdf.section_title(f"Step {interaction.step_id}: {interaction.action_type.upper()}")

            # Action details
            pdf.set_font('Arial', 'B', 9)
            pdf.cell(50, 5, 'Action:', 0, 0)
            pdf.set_font('Arial', '', 9)
            pdf.multi_cell(0, 5, interaction.notes)

            pdf.set_font('Arial', 'B', 9)
            pdf.cell(50, 5, 'Element:', 0, 0)
            pdf.set_font('Arial', '', 9)
            pdf.multi_cell(0, 5, interaction.element_text[:100])

            pdf.set_font('Arial', 'B', 9)
            pdf.cell(50, 5, 'URL:', 0, 0)
            pdf.set_font('Arial', '', 9)
            pdf.multi_cell(0, 5, interaction.url_after[:100])

            pdf.set_font('Arial', 'B', 9)
            pdf.cell(50, 5, 'Timestamp:', 0, 0)
            pdf.set_font('Arial', '', 9)
            pdf.cell(0, 5, interaction.timestamp, 0, 1)

            # Status
            pdf.set_font('Arial', 'B', 9)
            pdf.cell(50, 5, 'Status:', 0, 0)
            if interaction.success:
                pdf.set_text_color(0, 150, 0)
                pdf.cell(0, 5, 'Success', 0, 1)
            else:
                pdf.set_text_color(200, 0, 0)
                pdf.cell(0, 5, f'Failed - {interaction.error}', 0, 1)
            pdf.set_text_color(0, 0, 0)

            pdf.ln(3)

            # Screenshot
            if interaction.screenshot_path and os.path.exists(interaction.screenshot_path):
                try:
                    # Add screenshot (scaled to fit page width)
                    pdf.set_font('Arial', 'I', 9)
                    pdf.cell(0, 5, 'Screenshot:', 0, 1)

                    # Calculate dimensions to fit page
                    page_width = pdf.w - 30  # Margins
                    pdf.image(interaction.screenshot_path, x=15, w=page_width)
                    pdf.ln(5)

                except Exception as e:
                    self.logger.warning(f"Could not add screenshot: {e}")
                    pdf.set_font('Arial', 'I', 9)
                    pdf.cell(0, 5, '[Screenshot not available]', 0, 1)

            pdf.ln(5)

            # Add separator line
            pdf.set_draw_color(200, 200, 200)
            pdf.line(15, pdf.get_y(), pdf.w - 15, pdf.get_y())
            pdf.ln(5)

    def _add_observations_page(self, pdf: PDF, state_tracker: StateTracker):
        """Add observations and potential issues page."""
        pdf.add_page()
        pdf.chapter_title('Observations & Findings')

        # Failed interactions
        failed = state_tracker.get_failed_interactions()
        if failed:
            pdf.section_title('Failed Interactions')
            for interaction in failed:
                pdf.set_font('Arial', 'B', 9)
                pdf.cell(0, 5, f"Step {interaction.step_id}: {interaction.action_type}", 0, 1)
                pdf.set_font('Arial', '', 9)
                pdf.multi_cell(0, 5, f"  Error: {interaction.error}")
                pdf.multi_cell(0, 5, f"  Element: {interaction.element_text[:80]}")
                pdf.multi_cell(0, 5, f"  URL: {interaction.url_before[:80]}")
                pdf.ln(3)
        else:
            pdf.body_text('No failed interactions detected.')

        pdf.ln(5)

        # Popups handled
        pdf.section_title('Automated Actions')
        pdf.body_text(f"Total popups/modals handled automatically: {state_tracker.total_popups_handled}")

        pdf.ln(5)

        # Coverage
        pdf.section_title('Coverage Summary')
        pdf.body_text(
            f"Explored {len(state_tracker.visited_urls)} unique pages "
            f"through {state_tracker.current_step} interactions."
        )

        pdf.ln(5)

        # Recommendations
        pdf.section_title('Recommendations')
        recommendations = []

        if state_tracker.total_errors > 0:
            recommendations.append(
                f"- Investigate {state_tracker.total_errors} failed interaction(s) "
                "for potential bugs or UI issues."
            )

        if state_tracker.total_popups_handled > 5:
            recommendations.append(
                "- High number of popups detected. Consider reviewing user experience "
                "for excessive interruptions."
            )

        if len(state_tracker.visited_urls) < 5:
            recommendations.append(
                "- Limited page coverage. Consider increasing exploration depth or "
                "maximum steps for more thorough testing."
            )

        if not recommendations:
            recommendations.append(
                "- No major issues detected during automated exploration."
            )

        for rec in recommendations:
            pdf.body_text(rec)
            pdf.ln(2)
