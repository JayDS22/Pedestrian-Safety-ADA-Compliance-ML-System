"""
ADA Compliance Rule Engine
Evaluates detected infrastructure against ADA standards
"""

from typing import Dict, List
import logging

logger = logging.getLogger(__name__)


class ComplianceRuleEngine:
    """
    Rule-based engine for evaluating ADA compliance
    Based on 2010 ADA Standards + 2023 updates
    """
    
    # ADA Standards Constants
    MAX_CURB_RAMP_SLOPE = 8.33  # 1:12 ratio = 8.33%
    MAX_CROSS_SLOPE = 2.0       # 2%
    MIN_SIDEWALK_WIDTH = 36     # inches
    MIN_CLEAR_PATH = 36         # inches
    MAX_SURFACE_GAP = 0.5       # inches
    MAX_VERTICAL_CHANGE = 0.25  # inches without treatment
    MIN_LANDING_SIZE = 36       # inches x 36 inches
    
    def __init__(self):
        """Initialize compliance rules"""
        self.rules = self._load_rules()
        logger.info("Compliance engine initialized with ADA 2010 standards")
    
    def _load_rules(self) -> Dict:
        """Load all ADA compliance rules"""
        return {
            'curb_ramp_slope': {
                'standard': self.MAX_CURB_RAMP_SLOPE,
                'unit': 'percent',
                'description': 'Curb ramp running slope must not exceed 1:12 (8.33%)',
                'reference': 'ADAAG 406.2'
            },
            'cross_slope': {
                'standard': self.MAX_CROSS_SLOPE,
                'unit': 'percent',
                'description': 'Cross slope must not exceed 1:48 (2%)',
                'reference': 'ADAAG 406.3'
            },
            'sidewalk_width': {
                'standard': self.MIN_SIDEWALK_WIDTH,
                'unit': 'inches',
                'description': 'Minimum continuous clear width of 36 inches',
                'reference': 'ADAAG 403.5.1'
            },
            'surface_gap': {
                'standard': self.MAX_SURFACE_GAP,
                'unit': 'inches',
                'description': 'Surface openings not to exceed 0.5 inch',
                'reference': 'ADAAG 302.3'
            },
            'detectable_warning': {
                'required': True,
                'description': 'Detectable warning surfaces required at curb ramps',
                'reference': 'ADAAG 705'
            },
            'landing_size': {
                'standard': self.MIN_LANDING_SIZE,
                'unit': 'inches',
                'description': 'Landing must be 36" x 36" minimum',
                'reference': 'ADAAG 406.4'
            }
        }
    
    def evaluate(
        self,
        measurements: Dict,
        detections: List[Dict]
    ) -> List[Dict]:
        """
        Evaluate measurements against ADA standards
        
        Args:
            measurements: Dictionary of extracted measurements
            detections: List of detected objects
            
        Returns:
            List of violations found
        """
        violations = []
        
        # Evaluate each type of infrastructure
        for detection in detections:
            class_name = detection['class_name'].lower()
            
            if 'curb' in class_name or 'ramp' in class_name:
                violations.extend(self._check_curb_ramp(detection, measurements))
            
            elif 'sidewalk' in class_name or 'path' in class_name:
                violations.extend(self._check_sidewalk(detection, measurements))
            
            elif 'crosswalk' in class_name or 'crossing' in class_name:
                violations.extend(self._check_crosswalk(detection, measurements))
            
            elif 'surface' in class_name:
                violations.extend(self._check_surface_quality(detection, measurements))
        
        # Prioritize violations
        violations = self._prioritize_violations(violations)
        
        logger.info(f"Found {len(violations)} ADA violations")
        return violations
    
    def _check_curb_ramp(
        self,
        detection: Dict,
        measurements: Dict
    ) -> List[Dict]:
        """Check curb ramp compliance"""
        violations = []
        det_id = detection.get('id', id(detection))
        
        # Check slope
        if 'slope' in measurements:
            slope = measurements['slope'].get(det_id)
            if slope and slope > self.MAX_CURB_RAMP_SLOPE:
                violations.append({
                    'type': 'Curb Ramp Slope',
                    'severity': 'High',
                    'detected_value': f"{slope:.1f}% (1:{100/slope:.1f} ratio)",
                    'standard_value': f"≤{self.MAX_CURB_RAMP_SLOPE}% (1:12 ratio)",
                    'location': 'Detected curb ramp',
                    'reference': self.rules['curb_ramp_slope']['reference'],
                    'bbox': detection['bbox'],
                    'recommendation': 'Reconstruct ramp to meet 1:12 maximum slope',
                    'priority': 1
                })
        
        # Check cross slope
        if 'cross_slope' in measurements:
            cross_slope = measurements['cross_slope'].get(det_id)
            if cross_slope and cross_slope > self.MAX_CROSS_SLOPE:
                violations.append({
                    'type': 'Cross Slope',
                    'severity': 'High',
                    'detected_value': f"{cross_slope:.1f}%",
                    'standard_value': f"≤{self.MAX_CROSS_SLOPE}%",
                    'location': 'Curb ramp cross slope',
                    'reference': self.rules['cross_slope']['reference'],
                    'bbox': detection['bbox'],
                    'recommendation': 'Adjust cross slope to maximum 2%',
                    'priority': 1
                })
        
        # Check detectable warnings
        if 'detectable_warning' in measurements:
            has_warning = measurements['detectable_warning'].get(det_id, False)
            if not has_warning:
                violations.append({
                    'type': 'Detectable Warning',
                    'severity': 'High',
                    'detected_value': 'Missing',
                    'standard_value': 'Required at all curb ramps',
                    'location': 'Curb ramp',
                    'reference': self.rules['detectable_warning']['reference'],
                    'bbox': detection['bbox'],
                    'recommendation': 'Install truncated dome detectable warning surface',
                    'priority': 1
                })
        
        # Check landing size
        if 'landing_size' in measurements:
            landing = measurements['landing_size'].get(det_id)
            if landing and (landing[0] < self.MIN_LANDING_SIZE or 
                          landing[1] < self.MIN_LANDING_SIZE):
                violations.append({
                    'type': 'Landing Size',
                    'severity': 'Medium',
                    'detected_value': f"{landing[0]}\" x {landing[1]}\"",
                    'standard_value': f"≥{self.MIN_LANDING_SIZE}\" x {self.MIN_LANDING_SIZE}\"",
                    'location': 'Curb ramp landing',
                    'reference': self.rules['landing_size']['reference'],
                    'bbox': detection['bbox'],
                    'recommendation': 'Expand landing to minimum 36" x 36"',
                    'priority': 2
                })
        
        return violations
    
    def _check_sidewalk(
        self,
        detection: Dict,
        measurements: Dict
    ) -> List[Dict]:
        """Check sidewalk compliance"""
        violations = []
        det_id = detection.get('id', id(detection))
        
        # Check width
        if 'width' in measurements:
            width = measurements['width'].get(det_id)
            if width and width < self.MIN_SIDEWALK_WIDTH:
                violations.append({
                    'type': 'Sidewalk Width',
                    'severity': 'Medium',
                    'detected_value': f"{width:.0f} inches",
                    'standard_value': f"Minimum {self.MIN_SIDEWALK_WIDTH} inches",
                    'location': 'Sidewalk',
                    'reference': self.rules['sidewalk_width']['reference'],
                    'bbox': detection['bbox'],
                    'recommendation': 'Widen sidewalk to minimum 36 inches',
                    'priority': 2
                })
        
        # Check cross slope
        if 'cross_slope' in measurements:
            cross_slope = measurements['cross_slope'].get(det_id)
            if cross_slope and cross_slope > self.MAX_CROSS_SLOPE:
                violations.append({
                    'type': 'Cross Slope',
                    'severity': 'High',
                    'detected_value': f"{cross_slope:.1f}%",
                    'standard_value': f"Maximum {self.MAX_CROSS_SLOPE}%",
                    'location': 'Sidewalk',
                    'reference': self.rules['cross_slope']['reference'],
                    'bbox': detection['bbox'],
                    'recommendation': 'Regrade sidewalk to reduce cross slope',
                    'priority': 1
                })
        
        return violations
    
    def _check_crosswalk(
        self,
        detection: Dict,
        measurements: Dict
    ) -> List[Dict]:
        """Check crosswalk compliance"""
        violations = []
        det_id = detection.get('id', id(detection))
        
        # Check for curb ramps at crosswalk
        if 'has_curb_ramps' in measurements:
            has_ramps = measurements['has_curb_ramps'].get(det_id, False)
            if not has_ramps:
                violations.append({
                    'type': 'Missing Curb Ramps',
                    'severity': 'High',
                    'detected_value': 'No curb ramps detected',
                    'standard_value': 'Curb ramps required at all crossings',
                    'location': 'Crosswalk',
                    'reference': 'ADAAG 406',
                    'bbox': detection['bbox'],
                    'recommendation': 'Install compliant curb ramps',
                    'priority': 1
                })
        
        # Check marking visibility
        if 'marking_quality' in measurements:
            quality = measurements['marking_quality'].get(det_id)
            if quality and quality < 0.6:  # Quality score 0-1
                violations.append({
                    'type': 'Crosswalk Markings',
                    'severity': 'Medium',
                    'detected_value': f"Quality: {quality*100:.0f}%",
                    'standard_value': 'Clear and visible markings required',
                    'location': 'Crosswalk',
                    'reference': 'MUTCD Section 3B.18',
                    'bbox': detection['bbox'],
                    'recommendation': 'Repaint crosswalk markings',
                    'priority': 2
                })
        
        return violations
    
    def _check_surface_quality(
        self,
        detection: Dict,
        measurements: Dict
    ) -> List[Dict]:
        """Check surface quality compliance"""
        violations = []
        det_id = detection.get('id', id(detection))
        
        # Check for cracks and gaps
        if 'max_gap' in measurements:
            max_gap = measurements['max_gap'].get(det_id)
            if max_gap and max_gap > self.MAX_SURFACE_GAP:
                violations.append({
                    'type': 'Surface Quality',
                    'severity': 'Medium',
                    'detected_value': f"Gaps up to {max_gap:.2f} inches",
                    'standard_value': f"Maximum {self.MAX_SURFACE_GAP} inch",
                    'location': 'Surface',
                    'reference': self.rules['surface_gap']['reference'],
                    'bbox': detection['bbox'],
                    'recommendation': 'Repair or replace damaged surface',
                    'priority': 3
                })
        
        # Check for trip hazards
        if 'vertical_change' in measurements:
            vertical = measurements['vertical_change'].get(det_id)
            if vertical and vertical > self.MAX_VERTICAL_CHANGE:
                violations.append({
                    'type': 'Trip Hazard',
                    'severity': 'High',
                    'detected_value': f"{vertical:.2f} inch vertical change",
                    'standard_value': f"Maximum {self.MAX_VERTICAL_CHANGE} inch",
                    'location': 'Surface',
                    'reference': 'ADAAG 303.2',
                    'bbox': detection['bbox'],
                    'recommendation': 'Bevel edges or install ramp',
                    'priority': 1
                })
        
        return violations
    
    def _prioritize_violations(self, violations: List[Dict]) -> List[Dict]:
        """
        Assign priority scores and add cost estimates
        Priority 1 = Critical (safety hazard)
        Priority 2 = Important (accessibility barrier)
        Priority 3 = Moderate (minor compliance issue)
        """
        # Cost estimates for different violation types
        cost_estimates = {
            'Curb Ramp Slope': 2500,
            'Cross Slope': 3200,
            'Sidewalk Width': 1800,
            'Detectable Warning': 800,
            'Surface Quality': 2200,
            'Landing Size': 1500,
            'Missing Curb Ramps': 3500,
            'Crosswalk Markings': 400,
            'Trip Hazard': 1200
        }
        
        for violation in violations:
            # Add cost estimate
            viol_type = violation['type']
            violation['cost'] = cost_estimates.get(viol_type, 1000)
            
            # Ensure priority is set
            if 'priority' not in violation:
                if violation['severity'] == 'High':
                    violation['priority'] = 1
                elif violation['severity'] == 'Medium':
                    violation['priority'] = 2
                else:
                    violation['priority'] = 3
        
        # Sort by priority, then by cost
        violations.sort(key=lambda x: (x['priority'], -x['cost']))
        
        return violations
