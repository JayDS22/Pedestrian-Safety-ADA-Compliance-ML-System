"""
Report Generation Module
Generates PDF reports and exports for ADA compliance assessments
"""

from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, Image
from reportlab.lib import colors
from datetime import datetime
from pathlib import Path
from typing import Dict, List
import logging

logger = logging.getLogger(__name__)


class ReportGenerator:
    """
    Generate professional ADA compliance reports
    """
    
    def __init__(self, output_dir: str = "reports"):
        """
        Initialize report generator
        
        Args:
            output_dir: Directory to save generated reports
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
        logger.info(f"Report generator initialized, output: {self.output_dir}")
    
    def _setup_custom_styles(self):
        """Setup custom paragraph styles"""
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1e40af'),
            spaceAfter=30,
            alignment=1  # Center
        ))
        
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#2563eb'),
            spaceAfter=12,
            spaceBefore=12
        ))
        
        self.styles.add(ParagraphStyle(
            name='ViolationTitle',
            parent=self.styles['Heading3'],
            fontSize=12,
            textColor=colors.HexColor('#dc2626'),
            spaceAfter=6
        ))
    
    def generate_pdf(
        self,
        results: Dict,
        output_filename: str = None
    ) -> str:
        """
        Generate comprehensive PDF report
        
        Args:
            results: Analysis results dictionary
            output_filename: Custom filename (optional)
            
        Returns:
            Path to generated PDF file
        """
        if output_filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_filename = f"ada_compliance_report_{timestamp}.pdf"
        
        output_path = self.output_dir / output_filename
        
        # Create PDF document
        doc = SimpleDocTemplate(
            str(output_path),
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=18
        )
        
        # Build content
        story = []
        
        # Title page
        story.extend(self._create_title_page(results))
        story.append(PageBreak())
        
        # Executive summary
        story.extend(self._create_executive_summary(results))
        story.append(PageBreak())
        
        # Detailed violations
        story.extend(self._create_violations_section(results))
        story.append(PageBreak())
        
        # Cost analysis
        story.extend(self._create_cost_analysis(results))
        story.append(PageBreak())
        
        # Recommendations
        story.extend(self._create_recommendations(results))
        
        # Build PDF
        doc.build(story)
        
        logger.info(f"PDF report generated: {output_path}")
        return str(output_path)
    
    def _create_title_page(self, results: Dict) -> List:
        """Create report title page"""
        elements = []
        
        # Title
        title = Paragraph(
            "ADA Compliance Assessment Report",
            self.styles['CustomTitle']
        )
        elements.append(title)
        elements.append(Spacer(1, 0.3*inch))
        
        # Subtitle
        subtitle = Paragraph(
            "Pedestrian Infrastructure Evaluation",
            self.styles['Heading2']
        )
        elements.append(subtitle)
        elements.append(Spacer(1, 0.5*inch))
        
        # Report details
        location = results.get('location', 'N/A')
        timestamp = results.get('timestamp', datetime.now().isoformat())
        
        details = [
            ['Location:', location],
            ['Date:', datetime.fromisoformat(timestamp).strftime('%B %d, %Y')],
            ['Time:', datetime.fromisoformat(timestamp).strftime('%I:%M %p')],
            ['Compliance Score:', f"{results['compliance_score']}%"],
            ['Total Violations:', str(len(results['violations']))]
        ]
        
        table = Table(details, colWidths=[2*inch, 4*inch])
        table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 12),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#4b5563')),
            ('TEXTCOLOR', (1, 0), (1, -1), colors.HexColor('#111827')),
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ]))
        
        elements.append(table)
        elements.append(Spacer(1, 1*inch))
        
        # Disclaimer
        disclaimer = Paragraph(
            "<i>This report was generated using AI-powered computer vision analysis. "
            "All measurements and assessments should be verified by qualified professionals "
            "before making final compliance decisions.</i>",
            self.styles['Normal']
        )
        elements.append(disclaimer)
        
        return elements
    
    def _create_executive_summary(self, results: Dict) -> List:
        """Create executive summary section"""
        elements = []
        
        elements.append(Paragraph("Executive Summary", self.styles['SectionHeader']))
        elements.append(Spacer(1, 0.2*inch))
        
        # Summary metrics
        summary_data = [
            ['Metric', 'Value', 'Status'],
            ['Compliance Score', f"{results['compliance_score']}%", 
             self._get_status(results['compliance_score'])],
            ['Total Violations', str(len(results['violations'])),
             'Critical' if len(results['violations']) > 5 else 'Moderate'],
            ['Estimated Cost', f"${results['total_cost']:,}",
             'Budget Required'],
            ['Timeline', results['estimated_timeline'],
             'Planning Phase']
        ]
        
        table = Table(summary_data, colWidths=[2*inch, 1.5*inch, 2*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2563eb')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        elements.append(table)
        elements.append(Spacer(1, 0.3*inch))
        
        # Key findings
        findings_text = self._generate_findings_text(results)
        findings = Paragraph(findings_text, self.styles['Normal'])
        elements.append(findings)
        
        return elements
    
    def _create_violations_section(self, results: Dict) -> List:
        """Create detailed violations section"""
        elements = []
        
        elements.append(Paragraph("Detailed Violations", self.styles['SectionHeader']))
        elements.append(Spacer(1, 0.2*inch))
        
        violations = results['violations']
        
        if not violations:
            elements.append(Paragraph(
                "No ADA violations detected. Infrastructure meets compliance standards.",
                self.styles['Normal']
            ))
            return elements
        
        # Group by severity
        high = [v for v in violations if v['severity'] == 'High']
        medium = [v for v in violations if v['severity'] == 'Medium']
        low = [v for v in violations if v['severity'] == 'Low']
        
        for severity, viols in [('High', high), ('Medium', medium), ('Low', low)]:
            if not viols:
                continue
            
            elements.append(Paragraph(
                f"{severity} Priority Violations ({len(viols)})",
                self.styles['Heading3']
            ))
            elements.append(Spacer(1, 0.1*inch))
            
            for i, violation in enumerate(viols, 1):
                # Violation details
                viol_data = [
                    ['Type:', violation['type']],
                    ['Location:', violation['location']],
                    ['Detected:', violation['detected_value']],
                    ['ADA Standard:', violation['standard_value']],
                    ['Cost Estimate:', f"${violation['cost']:,}"],
                    ['Recommendation:', violation.get('recommendation', 'Remediation required')]
                ]
                
                table = Table(viol_data, colWidths=[1.5*inch, 4.5*inch])
                table.setStyle(TableStyle([
                    ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, -1), 10),
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ]))
                
                elements.append(table)
                elements.append(Spacer(1, 0.15*inch))
        
        return elements
    
    def _create_cost_analysis(self, results: Dict) -> List:
        """Create cost analysis section"""
        elements = []
        
        elements.append(Paragraph("Cost Analysis & Budget", self.styles['SectionHeader']))
        elements.append(Spacer(1, 0.2*inch))
        
        # Cost breakdown by type
        type_costs = {}
        for violation in results['violations']:
            viol_type = violation['type']
            cost = violation.get('cost', 0)
            type_costs[viol_type] = type_costs.get(viol_type, 0) + cost
        
        breakdown_data = [['Violation Type', 'Count', 'Total Cost']]
        for viol_type, cost in sorted(type_costs.items(), key=lambda x: x[1], reverse=True):
            count = sum(1 for v in results['violations'] if v['type'] == viol_type)
            breakdown_data.append([viol_type, str(count), f"${cost:,}"])
        
        # Add total row
        breakdown_data.append(['TOTAL', str(len(results['violations'])), 
                              f"${results['total_cost']:,}"])
        
        table = Table(breakdown_data, colWidths=[3*inch, 1*inch, 1.5*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2563eb')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#dbeafe')),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ]))
        
        elements.append(table)
        elements.append(Spacer(1, 0.3*inch))
        
        # Budget recommendation
        contingency = int(results['total_cost'] * 0.12)
        budget_text = (
            f"<b>Total Budget Required:</b> ${results['total_cost']:,}<br/>"
            f"<b>Recommended Contingency (12%):</b> ${contingency:,}<br/>"
            f"<b>Total Project Budget:</b> ${results['total_cost'] + contingency:,}<br/>"
            f"<b>Estimated Timeline:</b> {results['estimated_timeline']}"
        )
        
        elements.append(Paragraph(budget_text, self.styles['Normal']))
        
        return elements
    
    def _create_recommendations(self, results: Dict) -> List:
        """Create recommendations section"""
        elements = []
        
        elements.append(Paragraph("Recommendations & Next Steps", self.styles['SectionHeader']))
        elements.append(Spacer(1, 0.2*inch))
        
        recommendations = [
            "1. <b>Immediate Actions</b> - Address all High priority violations within 30-60 days",
            "2. <b>Phased Approach</b> - Develop multi-year capital improvement plan for Medium/Low priority items",
            "3. <b>Grant Funding</b> - Apply for federal/state accessibility grants using this report",
            "4. <b>Professional Verification</b> - Have licensed engineers verify measurements and costs",
            "5. <b>Community Engagement</b> - Solicit input from disability advocacy groups",
            "6. <b>Ongoing Monitoring</b> - Conduct annual accessibility audits",
            "7. <b>Documentation</b> - Maintain records of all remediation efforts for compliance"
        ]
        
        for rec in recommendations:
            elements.append(Paragraph(rec, self.styles['Normal']))
            elements.append(Spacer(1, 0.1*inch))
        
        elements.append(Spacer(1, 0.3*inch))
        
        # Contact info
        contact = Paragraph(
            "<b>For Questions or Support:</b><br/>"
            "ADA Compliance Assessment System<br/>"
            "Email: support@ada-compliance.com<br/>"
            "Phone: (555) 123-4567",
            self.styles['Normal']
        )
        elements.append(contact)
        
        return elements
    
    def _get_status(self, score: int) -> str:
        """Get status text based on compliance score"""
        if score >= 90:
            return 'Excellent'
        elif score >= 75:
            return 'Good'
        elif score >= 60:
            return 'Needs Improvement'
        else:
            return 'Critical'
    
    def _generate_findings_text(self, results: Dict) -> str:
        """Generate findings summary text"""
        score = results['compliance_score']
        num_violations = len(results['violations'])
        
        if score >= 90:
            summary = "The assessed infrastructure demonstrates excellent ADA compliance with minimal violations."
        elif score >= 75:
            summary = "The infrastructure shows good overall compliance but has areas requiring attention."
        elif score >= 60:
            summary = "Multiple compliance issues were identified that require remediation to meet ADA standards."
        else:
            summary = "Critical compliance deficiencies were found that pose significant accessibility barriers."
        
        high_priority = sum(1 for v in results['violations'] if v['severity'] == 'High')
        
        if high_priority > 0:
            summary += f" There are {high_priority} high-priority violations requiring immediate attention."
        
        return summary
    
    def export_csv(self, results: Dict, output_filename: str = None) -> str:
        """
        Export violations to CSV format
        
        Args:
            results: Analysis results
            output_filename: Custom filename (optional)
            
        Returns:
            Path to CSV file
        """
        import csv
        
        if output_filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_filename = f"violations_{timestamp}.csv"
        
        output_path = self.output_dir / output_filename
        
        with open(output_path, 'w', newline='') as f:
            writer = csv.writer(f)
            
            # Header
            writer.writerow([
                'Type', 'Severity', 'Priority', 'Location',
                'Detected Value', 'Standard Value', 'Cost',
                'Recommendation'
            ])
            
            # Data rows
            for violation in results['violations']:
                writer.writerow([
                    violation['type'],
                    violation['severity'],
                    violation['priority'],
                    violation['location'],
                    violation['detected_value'],
                    violation['standard_value'],
                    violation['cost'],
                    violation.get('recommendation', '')
                ])
        
        logger.info(f"CSV export generated: {output_path}")
        return str(output_path)
    
    def export_geojson(self, results: Dict, output_filename: str = None) -> str:
        """
        Export violations to GeoJSON format for GIS integration
        
        Args:
            results: Analysis results
            output_filename: Custom filename (optional)
            
        Returns:
            Path to GeoJSON file
        """
        import json
        
        if output_filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_filename = f"violations_{timestamp}.geojson"
        
        output_path = self.output_dir / output_filename
        
        # Create GeoJSON structure
        geojson = {
            "type": "FeatureCollection",
            "features": []
        }
        
        # Add violations as features (with mock coordinates for demo)
        for i, violation in enumerate(results['violations']):
            feature = {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [-122.4194 + i*0.001, 37.7749 + i*0.001]  # Mock coords
                },
                "properties": {
                    "type": violation['type'],
                    "severity": violation['severity'],
                    "priority": violation['priority'],
                    "location": violation['location'],
                    "detected_value": violation['detected_value'],
                    "standard_value": violation['standard_value'],
                    "cost": violation['cost'],
                    "recommendation": violation.get('recommendation', '')
                }
            }
            geojson["features"].append(feature)
        
        with open(output_path, 'w') as f:
            json.dump(geojson, f, indent=2)
        
        logger.info(f"GeoJSON export generated: {output_path}")
        return str(output_path)
