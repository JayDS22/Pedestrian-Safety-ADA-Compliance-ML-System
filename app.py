"""
ADA Compliance Assessment System - Streamlit Dashboard
Main application entry point for interactive web interface
"""

import streamlit as st
import cv2
import numpy as np
from PIL import Image
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from pathlib import Path
import json
from datetime import datetime

# Import custom modules
from ada_compliance.analyzer import ComplianceAnalyzer
from ada_compliance.visualizer import ResultVisualizer
from ada_compliance.report_generator import ReportGenerator

# Page config
st.set_page_config(
    page_title="ADA Compliance System",
    page_icon="🚶",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main {
        padding: 0rem 1rem;
    }
    .stMetric {
        background-color: #f0f2f6;
        padding: 15px;
        border-radius: 10px;
    }
    </style>
    """, unsafe_allow_html=True)


class ADAComplianceApp:
    """Main application class for ADA Compliance System"""
    
    def __init__(self):
        self.analyzer = ComplianceAnalyzer()
        self.visualizer = ResultVisualizer()
        self.report_gen = ReportGenerator()
        
    def run(self):
        """Main application logic"""
        
        # Header
        col1, col2 = st.columns([3, 1])
        with col1:
            st.title("🚶 ADA Compliance Assessment System")
            st.markdown("*AI-Powered Pedestrian Infrastructure Analysis*")
        with col2:
            st.image("assets/logo.png", width=100) if Path("assets/logo.png").exists() else None
        
        st.divider()
        
        # Sidebar
        with st.sidebar:
            st.header("⚙️ Settings")
            
            confidence_threshold = st.slider(
                "Detection Confidence",
                min_value=0.1,
                max_value=0.95,
                value=0.6,
                step=0.05,
                help="Minimum confidence for object detection"
            )
            
            show_annotations = st.checkbox("Show Annotations", value=True)
            generate_report = st.checkbox("Auto-generate Report", value=False)
            
            st.divider()
            
            st.header("📊 Quick Stats")
            if 'total_analyzed' not in st.session_state:
                st.session_state.total_analyzed = 0
            st.metric("Images Analyzed", st.session_state.total_analyzed)
            
        # Main tabs
        tab1, tab2, tab3, tab4 = st.tabs([
            "📤 Upload & Analyze",
            "📋 Results & Violations",
            "🗺️ Heatmap",
            "📊 Analytics"
        ])
        
        with tab1:
            self.upload_analyze_tab(confidence_threshold, show_annotations, generate_report)
            
        with tab2:
            self.results_tab()
            
        with tab3:
            self.heatmap_tab()
            
        with tab4:
            self.analytics_tab()
    
    def upload_analyze_tab(self, confidence, show_annotations, generate_report):
        """Tab for uploading and analyzing images"""
        
        st.header("Upload Infrastructure Image")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            uploaded_file = st.file_uploader(
                "Choose an image...",
                type=['jpg', 'jpeg', 'png'],
                help="Upload sidewalk, curb ramp, or crosswalk image"
            )
            
            if uploaded_file:
                image = Image.open(uploaded_file)
                st.image(image, caption="Uploaded Image", use_column_width=True)
                
                location = st.text_input(
                    "Location (Optional)",
                    placeholder="e.g., Main St & 1st Ave"
                )
                
                if st.button("🔍 Analyze for ADA Compliance", type="primary", use_container_width=True):
                    self.analyze_image(image, location, confidence, show_annotations, generate_report)
        
        with col2:
            st.info("**Supported Infrastructure:**")
            st.markdown("""
            - ✅ Sidewalks
            - ✅ Curb Ramps
            - ✅ Crosswalks
            - ✅ Pedestrian Signals
            - ✅ Access Ramps
            - ✅ Pedestrian Paths
            """)
            
            st.warning("**Detection Capabilities:**")
            st.markdown("""
            - Slope measurements
            - Width measurements
            - Surface quality
            - Obstruction detection
            - Compliance scoring
            """)
    
    def analyze_image(self, image, location, confidence, show_annotations, generate_report):
        """Analyze uploaded image"""
        
        with st.spinner("🔍 Analyzing infrastructure..."):
            # Convert PIL to numpy
            img_array = np.array(image)
            
            # Run analysis
            results = self.analyzer.analyze(
                img_array,
                confidence_threshold=confidence,
                location=location
            )
            
            # Store in session state
            st.session_state.latest_results = results
            st.session_state.total_analyzed += 1
            
            # Display results
            st.success("✅ Analysis Complete!")
            
            # Show annotated image
            if show_annotations and results.get('annotated_image') is not None:
                st.subheader("Detected Violations")
                st.image(
                    results['annotated_image'],
                    caption="Infrastructure with ADA Violations Highlighted",
                    use_column_width=True
                )
            
            # Summary metrics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(
                    "Compliance Score",
                    f"{results['compliance_score']}%",
                    delta=f"{results['compliance_score'] - 80}% from target"
                )
            
            with col2:
                st.metric(
                    "Violations Found",
                    len(results['violations']),
                    delta=f"-{len(results['violations'])} to fix"
                )
            
            with col3:
                st.metric(
                    "Estimated Cost",
                    f"${results['total_cost']:,}",
                )
            
            with col4:
                st.metric(
                    "Timeline",
                    results['estimated_timeline']
                )
            
            # Generate report if requested
            if generate_report:
                with st.spinner("📄 Generating PDF report..."):
                    report_path = self.report_gen.generate_pdf(results)
                    
                    with open(report_path, 'rb') as f:
                        st.download_button(
                            "📥 Download Full Report (PDF)",
                            f,
                            file_name=f"ada_compliance_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                            mime="application/pdf",
                            use_container_width=True
                        )
    
    def results_tab(self):
        """Tab for displaying detailed results"""
        
        if 'latest_results' not in st.session_state:
            st.info("👆 Upload and analyze an image to see results here")
            return
        
        results = st.session_state.latest_results
        
        st.header("Detailed Violation Analysis")
        
        # Filters
        col1, col2, col3 = st.columns(3)
        
        with col1:
            severity_filter = st.multiselect(
                "Filter by Severity",
                ["High", "Medium", "Low"],
                default=["High", "Medium", "Low"]
            )
        
        with col2:
            sort_by = st.selectbox(
                "Sort By",
                ["Priority", "Cost", "Type"]
            )
        
        with col3:
            min_cost = st.number_input("Min Cost ($)", min_value=0, value=0)
        
        # Filter violations
        violations = results['violations']
        filtered = [
            v for v in violations 
            if v['severity'] in severity_filter and v['cost'] >= min_cost
        ]
        
        # Sort
        if sort_by == "Priority":
            filtered.sort(key=lambda x: x['priority'])
        elif sort_by == "Cost":
            filtered.sort(key=lambda x: x['cost'], reverse=True)
        else:
            filtered.sort(key=lambda x: x['type'])
        
        st.divider()
        
        # Display violations
        for idx, violation in enumerate(filtered, 1):
            with st.expander(
                f"**{idx}. {violation['type']}** - {violation['severity']} Priority",
                expanded=(idx <= 3)
            ):
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.markdown(f"**Location:** {violation['location']}")
                    st.markdown(f"**Detected:** {violation['detected_value']}")
                    st.markdown(f"**ADA Standard:** {violation['standard_value']}")
                    st.markdown(f"**Recommendation:** {violation.get('recommendation', 'Immediate remediation required')}")
                
                with col2:
                    st.metric("Remediation Cost", f"${violation['cost']:,}")
                    st.metric("Priority Level", violation['priority'])
                    
                    severity_color = {
                        "High": "🔴",
                        "Medium": "🟡",
                        "Low": "🟢"
                    }
                    st.markdown(f"{severity_color[violation['severity']]} **{violation['severity']} Severity**")
        
        st.divider()
        
        # Export options
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📊 Export to CSV", use_container_width=True):
                df = pd.DataFrame(filtered)
                csv = df.to_csv(index=False)
                st.download_button(
                    "Download CSV",
                    csv,
                    "violations.csv",
                    "text/csv",
                    use_container_width=True
                )
        
        with col2:
            if st.button("📄 Generate Full Report", use_container_width=True):
                st.info("Report generation feature coming soon!")
        
        with col3:
            if st.button("🗺️ Export to GIS", use_container_width=True):
                st.info("GIS export feature coming soon!")
    
    def heatmap_tab(self):
        """Tab for displaying risk heatmaps"""
        
        st.header("Accessibility Risk Heatmap")
        
        col1, col2 = st.columns([3, 1])
        
        with col2:
            st.subheader("Legend")
            st.markdown("🔴 **High Risk** - Critical violations")
            st.markdown("🟡 **Medium Risk** - Moderate issues")
            st.markdown("🟢 **Low Risk** - Minor concerns")
            
            st.divider()
            
            st.metric("High-Risk Areas", "12")
            st.metric("Network Gaps", "8")
            st.metric("Non-Compliant (mi)", "3.2")
        
        with col1:
            # Sample heatmap visualization
            st.info("🗺️ Interactive heatmap visualization would appear here")
            st.markdown("*Integrate with Folium/Plotly for live geospatial data*")
            
            # Sample data
            fig = go.Figure(data=go.Scattermapbox(
                lat=[37.7749, 37.7849, 37.7649],
                lon=[-122.4194, -122.4094, -122.4294],
                mode='markers',
                marker=dict(
                    size=20,
                    color=['red', 'yellow', 'green'],
                    opacity=0.7
                ),
                text=['High Risk', 'Medium Risk', 'Low Risk']
            ))
            
            fig.update_layout(
                mapbox_style="open-street-map",
                mapbox_center_lat=37.7749,
                mapbox_center_lon=-122.4194,
                mapbox_zoom=12,
                height=500
            )
            
            st.plotly_chart(fig, use_container_width=True)
    
    def analytics_tab(self):
        """Tab for system analytics and statistics"""
        
        st.header("System Analytics & Insights")
        
        # Sample analytics data
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Violation Type Distribution")
            
            violation_types = {
                "Curb Ramp Slope": 45,
                "Sidewalk Width": 32,
                "Cross Slope": 28,
                "Surface Quality": 23,
                "Detectable Warning": 18,
                "Others": 15
            }
            
            fig = px.pie(
                values=list(violation_types.values()),
                names=list(violation_types.keys()),
                title="Most Common Violations"
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("Cost by Severity")
            
            severity_costs = pd.DataFrame({
                'Severity': ['High', 'Medium', 'Low'],
                'Total Cost': [45000, 28000, 12000],
                'Count': [23, 35, 18]
            })
            
            fig = px.bar(
                severity_costs,
                x='Severity',
                y='Total Cost',
                color='Severity',
                color_discrete_map={
                    'High': 'red',
                    'Medium': 'orange',
                    'Low': 'green'
                },
                title="Remediation Cost by Severity"
            )
            st.plotly_chart(fig, use_container_width=True)
        
        st.divider()
        
        # Performance metrics
        st.subheader("System Performance")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Detection Accuracy", "94.2%", "+2.1%")
        
        with col2:
            st.metric("Avg. Processing Time", "73ms", "-12ms")
        
        with col3:
            st.metric("Assets Processed", "1,247", "+215")
        
        with col4:
            st.metric("False Positive Rate", "6.8%", "-1.2%")


# Main entry point
if __name__ == "__main__":
    app = ADAComplianceApp()
    app.run()
