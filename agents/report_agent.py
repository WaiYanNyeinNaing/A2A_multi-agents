# agents/report_agent.py
"""
Report Writing Agent using Google Gemini
- Specialized for creating comprehensive reports from research data
- Converts raw research into structured documents
- Supports multiple output formats (Markdown, HTML)
"""

import json
from typing import Dict, Any, List
from .base_agent import BaseAgent

class ReportAgent(BaseAgent):
    """
    Report Writing Agent specialized for creating comprehensive reports
    """
    
    def __init__(self):
        super().__init__("report_specialist")
    
    def write_research_report(self, research_data: str, report_type: str = "comprehensive") -> Dict[str, Any]:
        """
        Write a comprehensive report from research data.
        
        Args:
            research_data: Raw research data or findings (JSON string or text)
            report_type: Type of report (comprehensive, summary, executive, academic)
            
        Returns:
            Dict containing the formatted report
        """
        try:
            # Parse research data if it's JSON
            if isinstance(research_data, str):
                try:
                    parsed_data = json.loads(research_data)
                except json.JSONDecodeError:
                    parsed_data = {"content": research_data}
            else:
                parsed_data = research_data
            
            # Generate report based on type
            report_content = self._generate_report_content(parsed_data, report_type)
            
            # Format the report
            formatted_report = self._format_report(report_content, report_type)
            
            return self.create_success_response(
                report_id=self.generate_unique_id(),
                report_type=report_type,
                content=formatted_report,
                word_count=len(formatted_report.split()),
                sections=self._count_sections(formatted_report)
            )
            
        except Exception as e:
            return self.create_error_response(str(e), "report_generation_error")
    
    def convert_to_html(self, report_content: str) -> Dict[str, Any]:
        """
        Convert report content to HTML format.
        
        Args:
            report_content: Markdown or plain text report content
            
        Returns:
            Dict containing HTML formatted report
        """
        try:
            # Simple Markdown to HTML conversion
            html_content = self._markdown_to_html(report_content)
            
            return self.create_success_response(
                conversion_id=self.generate_unique_id(),
                format="html",
                content=html_content,
                original_length=len(report_content),
                html_length=len(html_content)
            )
            
        except Exception as e:
            return self.create_error_response(str(e), "html_conversion_error")
    
    def generate_executive_summary(self, full_report: str, max_length: int = 500) -> Dict[str, Any]:
        """
        Generate an executive summary from a full report.
        
        Args:
            full_report: Complete report content
            max_length: Maximum length of summary in words
            
        Returns:
            Dict containing executive summary
        """
        try:
            prompt = f"""
            Create an executive summary from this report. Keep it to {max_length} words maximum.
            Focus on key findings, main conclusions, and actionable insights.
            
            Report:
            {full_report}
            
            Executive Summary:
            """
            
            summary = self.call_gemini_api(prompt)
            
            return self.create_success_response(
                summary_id=self.generate_unique_id(),
                summary=summary,
                word_count=len(summary.split()),
                compression_ratio=len(summary.split()) / len(full_report.split())
            )
            
        except Exception as e:
            return self.create_error_response(str(e), "summary_generation_error")
    
    def create_slide_outline(self, report_content: str, num_slides: int = 10) -> Dict[str, Any]:
        """
        Create a presentation slide outline from report content.
        
        Args:
            report_content: Report content to convert
            num_slides: Target number of slides
            
        Returns:
            Dict containing slide outline
        """
        try:
            prompt = f"""
            Create a {num_slides}-slide presentation outline from this report:
            
            {report_content}
            
            Format as:
            Slide 1: Title
            - Bullet point 1
            - Bullet point 2
            
            Slide 2: Title
            - Bullet point 1
            - Bullet point 2
            
            Focus on key points and logical flow.
            """
            
            outline = self.call_gemini_api(prompt)
            
            return self.create_success_response(
                outline_id=self.generate_unique_id(),
                outline=outline,
                slide_count=num_slides,
                report_length=len(report_content.split())
            )
            
        except Exception as e:
            return self.create_error_response(str(e), "slide_outline_error")
    
    def _generate_report_content(self, data: Dict[str, Any], report_type: str) -> str:
        """Generate report content based on data and type."""
        
        if report_type == "executive":
            prompt = f"""
            Create a brief executive summary report from this data:
            {json.dumps(data, indent=2)}
            
            Format:
            # Executive Summary
            ## Key Findings
            ## Recommendations
            ## Conclusion
            """
        elif report_type == "academic":
            prompt = f"""
            Create an academic-style report from this data:
            {json.dumps(data, indent=2)}
            
            Format:
            # Abstract
            ## Introduction
            ## Methodology
            ## Findings
            ## Discussion
            ## Conclusion
            ## References
            """
        else:  # comprehensive
            prompt = f"""
            Create a comprehensive report from this research data:
            {json.dumps(data, indent=2)}
            
            Format:
            # Executive Summary
            ## Introduction
            ## Background
            ## Key Findings
            ## Analysis
            ## Implications
            ## Recommendations
            ## Conclusion
            
            Be thorough and include specific data points and sources where available.
            """
        
        try:
            return self.call_gemini_api(prompt)
        except:
            return f"# Report\n\nBased on the provided data, here are the key findings and analysis.\n\nData: {str(data)}"
    
    def _format_report(self, content: str, report_type: str) -> str:
        """Apply formatting based on report type."""
        # Add metadata header
        header = f"<!-- Report Type: {report_type} | Generated: {self.get_timestamp()} -->\n\n"
        return header + content
    
    def _count_sections(self, content: str) -> int:
        """Count the number of sections in the report."""
        return content.count('#')
    
    def _markdown_to_html(self, markdown: str) -> str:
        """Simple Markdown to HTML conversion."""
        html = markdown
        
        # Headers
        html = html.replace('# ', '<h1>').replace('\n# ', '</h1>\n<h1>')
        html = html.replace('## ', '<h2>').replace('\n## ', '</h2>\n<h2>')
        html = html.replace('### ', '<h3>').replace('\n### ', '</h3>\n<h3>')
        
        # Bold and italic
        html = html.replace('**', '<strong>').replace('**', '</strong>')
        html = html.replace('*', '<em>').replace('*', '</em>')
        
        # Line breaks
        html = html.replace('\n\n', '</p>\n<p>')
        
        # Wrap in basic HTML structure
        html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Research Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }}
        h1, h2, h3 {{ color: #333; }}
        p {{ line-height: 1.6; }}
    </style>
</head>
<body>
    <p>{html}</p>
</body>
</html>"""
        
        return html
    
    def get_agent_info(self) -> Dict[str, Any]:
        """Get information about this agent."""
        return {
            "name": "Report Writing Specialist",
            "type": "report",
            "model": self.model_name,
            "capabilities": ["write_research_report", "convert_to_html", "generate_executive_summary", "create_slide_outline"],
            "supported_formats": ["markdown", "html"],
            "report_types": ["comprehensive", "executive", "academic", "summary"],
            "status": "ready"
        }