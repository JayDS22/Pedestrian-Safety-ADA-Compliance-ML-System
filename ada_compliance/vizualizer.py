"""
Visualization Module
Generate heatmaps, charts, and visual analysis tools
"""

import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from typing import Dict, List
import folium
from folium.plugins import HeatMap
import logging

logger = logging.getLogger(__name__)


class ResultVisualizer:
    """
    Create visualizations for ADA compliance analysis
    """
    
    def __init__(self):
        """Initialize visualizer"""
        sns.set_theme(style="whitegrid")
        logger.info("Visualizer initialized")
    
    def create_compliance_heatmap(
        self,
        violations_data: List[Dict],
        center_coords: tuple = (37.7749, -122.4194),
        zoom_start: int = 13
    ) -> folium.Map:
        """
        Create interactive heatmap of violations
        
        Args:
            violations_data: List of violations with coordinates
            center_coords: Map center (lat, lon)
            zoom_start: Initial zoom level
            
        Returns:
            Folium map object
        """
        # Create base map
        m = folium.Map(
            location=center_coords,
            zoom_start=zoom_start,
            tiles='OpenStreetMap'
        )
        
        # Prepare heatmap data
        heat_data = []
        for violation in violations_data:
            # In real implementation, extract actual coordinates
            # For demo, use mock coordinates
            lat = center_coords[0] + np.random.uniform(-0.01, 0.01)
            lon = center_coords[1] + np.random.uniform(-0.01, 0.01)
            
            # Weight by severity
            weight = {'High': 1.0, 'Medium': 0.6, 'Low': 0.3}.get(
                violation['severity'], 0.5
            )
            
            heat_data.append([lat, lon, weight])
        
        # Add heatmap layer
        HeatMap(heat_data).add_to(m)
        
        # Add violation markers
        for i, violation in enumerate(violations_data):
            lat = center_coords[0] + np.random.uniform(-0.01, 0.01)
            lon = center_coords[1] + np.random.uniform(-0.01, 0.01)
            
            color = {
                'High': 'red',
                'Medium': 'orange',
                'Low': 'yellow'
            }.get(violation['severity'], 'blue')
            
            folium.CircleMarker(
                location=[lat, lon],
                radius=8,
                popup=f"{violation['type']}<br/>{violation['location']}",
                color=color,
                fill=True,
                fillColor=color
            ).add_to(m)
        
        logger.info(f"Generated heatmap with {len(violations_data)} violations")
        return m
    
    def plot_violation_distribution(
        self,
        violations: List[Dict],
        save_path: str = None
    ):
        """
        Create bar chart of violation types
        
        Args:
            violations: List of violations
            save_path: Path to save figure (optional)
        """
        # Count violations by type
        type_counts = {}
        for v in violations:
            vtype = v['type']
            type_counts[vtype] = type_counts.get(vtype, 0) + 1
        
        # Sort by count
        sorted_types = sorted(type_counts.items(), key=lambda x: x[1], reverse=True)
        types = [t[0] for t in sorted_types]
        counts = [t[1] for t in sorted_types]
        
        # Create plot
        fig, ax = plt.subplots(figsize=(10, 6))
        bars = ax.barh(types, counts, color='steelblue')
        
        # Color by severity
        for i, vtype in enumerate(types):
            # Find typical severity for this type
            severity_counts = {'High': 0, 'Medium': 0, 'Low': 0}
            for v in violations:
                if v['type'] == vtype:
                    severity_counts[v['severity']] += 1
            
            dominant_severity = max(severity_counts.items(), key=lambda x: x[1])[0]
            color = {'High': '#ef4444', 'Medium': '#f59e0b', 'Low': '#10b981'}[dominant_severity]
            bars[i].set_color(color)
        
        ax.set_xlabel('Number of Violations', fontsize=12)
        ax.set_title('ADA Violations by Type', fontsize=14, fontweight='bold')
        ax.grid(axis='x', alpha=0.3)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            logger.info(f"Saved violation distribution plot to {save_path}")
        
        return fig
    
    def plot_cost_by_severity(
        self,
        violations: List[Dict],
        save_path: str = None
    ):
        """
        Create pie chart of costs by severity
        
        Args:
            violations: List of violations
            save_path: Path to save figure (optional)
        """
        # Calculate costs by severity
        severity_costs = {'High': 0, 'Medium': 0, 'Low': 0}
        for v in violations:
            severity_costs[v['severity']] += v.get('cost', 0)
        
        # Filter out zero values
        labels = []
        sizes = []
        colors_list = []
        
        color_map = {
            'High': '#ef4444',
            'Medium': '#f59e0b',
            'Low': '#10b981'
        }
        
        for severity in ['High', 'Medium', 'Low']:
            if severity_costs[severity] > 0:
                labels.append(f"{severity} (${severity_costs[severity]:,})")
                sizes.append(severity_costs[severity])
                colors_list.append(color_map[severity])
        
        # Create plot
        fig, ax = plt.subplots(figsize=(8, 8))
        wedges, texts, autotexts = ax.pie(
            sizes,
            labels=labels,
            colors=colors_list,
            autopct='%1.1f%%',
            startangle=90,
            textprops={'fontsize': 11}
        )
        
        # Enhance text
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
        
        ax.set_title('Remediation Cost by Severity', fontsize=14, fontweight='bold')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            logger.info(f"Saved cost distribution plot to {save_path}")
        
        return fig
    
    def plot_priority_timeline(
        self,
        violations: List[Dict],
        save_path: str = None
    ):
        """
        Create timeline visualization for remediation priorities
        
        Args:
            violations: List of violations
            save_path: Path to save figure (optional)
        """
        # Group by priority
        priority_groups = {1: [], 2: [], 3: []}
        for v in violations:
            priority = v.get('priority', 2)
            priority_groups[priority].append(v)
        
        # Calculate cumulative costs
        priorities = []
        costs = []
        colors_list = []
        
        for priority in [1, 2, 3]:
            if priority_groups[priority]:
                total_cost = sum(v.get('cost', 0) for v in priority_groups[priority])
                priorities.append(f"Priority {priority}")
                costs.append(total_cost)
                colors_list.append(['#ef4444', '#f59e0b', '#10b981'][priority-1])
        
        # Create plot
        fig, ax = plt.subplots(figsize=(10, 6))
        bars = ax.bar(priorities, costs, color=colors_list, edgecolor='black', linewidth=1.5)
        
        # Add value labels on bars
        for bar in bars:
            height = bar.get_height()
            ax.text(
                bar.get_x() + bar.get_width()/2.,
                height,
                f'${height:,.0f}',
                ha='center',
                va='bottom',
                fontsize=11,
                fontweight='bold'
            )
        
        ax.set_ylabel('Total Cost ($)', fontsize=12)
        ax.set_title('Remediation Cost by Priority Level', fontsize=14, fontweight='bold')
        ax.grid(axis='y', alpha=0.3)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            logger.info(f"Saved priority timeline plot to {save_path}")
        
        return fig
    
    def generate_dashboard(
        self,
        results: Dict,
        output_path: str = "dashboard.png"
    ):
        """
        Generate comprehensive dashboard with multiple visualizations
        
        Args:
            results: Analysis results
            output_path: Path to save dashboard
        """
        violations = results['violations']
        
        # Create figure with subplots
        fig = plt.figure(figsize=(16, 10))
        gs = fig.add_gridspec(2, 2, hspace=0.3, wspace=0.3)
        
        # 1. Violation distribution
        ax1 = fig.add_subplot(gs[0, 0])
        type_counts = {}
        for v in violations:
            vtype = v['type']
            type_counts[vtype] = type_counts.get(vtype, 0) + 1
        
        sorted_types = sorted(type_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        types = [t[0] for t in sorted_types]
        counts = [t[1] for t in sorted_types]
        
        ax1.barh(types, counts, color='steelblue')
        ax1.set_xlabel('Count')
        ax1.set_title('Top Violation Types', fontweight='bold')
        ax1.grid(axis='x', alpha=0.3)
        
        # 2. Cost by severity
        ax2 = fig.add_subplot(gs[0, 1])
        severity_costs = {'High': 0, 'Medium': 0, 'Low': 0}
        for v in violations:
            severity_costs[v['severity']] += v.get('cost', 0)
        
        colors = ['#ef4444', '#f59e0b', '#10b981']
        ax2.pie(
            [severity_costs[s] for s in ['High', 'Medium', 'Low']],
            labels=[f"{s}\n${severity_costs[s]:,}" for s in ['High', 'Medium', 'Low']],
            colors=colors,
            autopct='%1.1f%%',
            startangle=90
        )
        ax2.set_title('Cost by Severity', fontweight='bold')
        
        # 3. Priority distribution
        ax3 = fig.add_subplot(gs[1, 0])
        priority_counts = {1: 0, 2: 0, 3: 0}
        for v in violations:
            priority_counts[v.get('priority', 2)] += 1
        
        ax3.bar(
            ['Priority 1', 'Priority 2', 'Priority 3'],
            [priority_counts[p] for p in [1, 2, 3]],
            color=['#ef4444', '#f59e0b', '#10b981']
        )
        ax3.set_ylabel('Count')
        ax3.set_title('Violations by Priority', fontweight='bold')
        ax3.grid(axis='y', alpha=0.3)
        
        # 4. Summary metrics
        ax4 = fig.add_subplot(gs[1, 1])
        ax4.axis('off')
        
        summary_text = f"""
        COMPLIANCE SUMMARY
        
        Compliance Score: {results['compliance_score']}%
        Total Violations: {len(violations)}
        Total Cost: ${results['total_cost']:,}
        Timeline: {results['estimated_timeline']}
        
        High Priority: {priority_counts[1]}
        Medium Priority: {priority_counts[2]}
        Low Priority: {priority_counts[3]}
        """
        
        ax4.text(
            0.1, 0.5,
            summary_text,
            fontsize=12,
            verticalalignment='center',
            fontfamily='monospace',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5)
        )
        
        fig.suptitle(
            'ADA Compliance Assessment Dashboard',
            fontsize=16,
            fontweight='bold'
        )
        
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        logger.info(f"Saved dashboard to {output_path}")
        
        return fig
