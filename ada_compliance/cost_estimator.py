"""
Cost Estimation Module
Estimates remediation costs and timelines for ADA violations
"""

from typing import Dict, List
import logging

logger = logging.getLogger(__name__)


class CostEstimator:
    """
    Estimate costs and timelines for ADA compliance remediation
    Based on typical infrastructure improvement costs
    """
    
    # Base cost estimates (in USD)
    BASE_COSTS = {
        'Curb Ramp Slope': {
            'min': 2000,
            'max': 3500,
            'typical': 2500,
            'unit': 'per ramp',
            'labor_hours': 16
        },
        'Cross Slope': {
            'min': 2500,
            'max': 4000,
            'typical': 3200,
            'unit': 'per section',
            'labor_hours': 20
        },
        'Sidewalk Width': {
            'min': 1500,
            'max': 2500,
            'typical': 1800,
            'unit': 'per linear foot',
            'labor_hours': 12
        },
        'Detectable Warning': {
            'min': 600,
            'max': 1200,
            'typical': 800,
            'unit': 'per installation',
            'labor_hours': 4
        },
        'Surface Quality': {
            'min': 1800,
            'max': 3000,
            'typical': 2200,
            'unit': 'per section',
            'labor_hours': 14
        },
        'Landing Size': {
            'min': 1200,
            'max': 2000,
            'typical': 1500,
            'unit': 'per landing',
            'labor_hours': 10
        },
        'Missing Curb Ramps': {
            'min': 3000,
            'max': 4500,
            'typical': 3500,
            'unit': 'per ramp',
            'labor_hours': 24
        },
        'Crosswalk Markings': {
            'min': 300,
            'max': 600,
            'typical': 400,
            'unit': 'per crossing',
            'labor_hours': 2
        },
        'Trip Hazard': {
            'min': 800,
            'max': 1800,
            'typical': 1200,
            'unit': 'per repair',
            'labor_hours': 8
        }
    }
    
    # Complexity multipliers
    COMPLEXITY_FACTORS = {
        'urban_high_traffic': 1.3,
        'historic_district': 1.5,
        'utility_conflicts': 1.4,
        'drainage_issues': 1.2,
        'standard': 1.0
    }
    
    def __init__(self):
        """Initialize cost estimator"""
        logger.info("Cost estimator initialized")
    
    def estimate(
        self,
        violations: List[Dict],
        complexity: str = 'standard'
    ) -> Dict:
        """
        Estimate total remediation costs and timeline
        
        Args:
            violations: List of ADA violations
            complexity: Project complexity factor
            
        Returns:
            Dictionary with cost breakdown and timeline
        """
        if not violations:
            return {
                'total_cost': 0,
                'timeline': 'N/A',
                'breakdown': [],
                'labor_hours': 0
            }
        
        # Get complexity multiplier
        multiplier = self.COMPLEXITY_FACTORS.get(complexity, 1.0)
        
        # Calculate costs for each violation
        breakdown = []
        total_cost = 0
        total_labor_hours = 0
        
        for violation in violations:
            viol_type = violation['type']
            
            if viol_type in self.BASE_COSTS:
                cost_info = self.BASE_COSTS[viol_type]
                
                # Use typical cost with complexity adjustment
                base_cost = cost_info['typical']
                adjusted_cost = int(base_cost * multiplier)
                
                # Add to violation record
                violation['cost'] = adjusted_cost
                violation['labor_hours'] = cost_info['labor_hours']
                
                breakdown.append({
                    'type': viol_type,
                    'cost': adjusted_cost,
                    'unit': cost_info['unit'],
                    'labor_hours': cost_info['labor_hours'],
                    'priority': violation.get('priority', 2)
                })
                
                total_cost += adjusted_cost
                total_labor_hours += cost_info['labor_hours']
            else:
                # Default cost for unknown violation types
                default_cost = 1000
                violation['cost'] = default_cost
                violation['labor_hours'] = 8
                
                total_cost += default_cost
                total_labor_hours += 8
        
        # Estimate timeline
        timeline = self._estimate_timeline(total_labor_hours, len(violations))
        
        # Add contingency (typically 10-15%)
        contingency = int(total_cost * 0.12)
        total_with_contingency = total_cost + contingency
        
        return {
            'total_cost': total_cost,
            'contingency': contingency,
            'total_with_contingency': total_with_contingency,
            'timeline': timeline,
            'breakdown': breakdown,
            'labor_hours': total_labor_hours,
            'complexity_factor': multiplier
        }
    
    def _estimate_timeline(
        self,
        total_labor_hours: int,
        num_violations: int
    ) -> str:
        """
        Estimate project timeline based on labor hours
        Assumes crew of 2-3 workers, 8-hour days
        """
        # Crew size and hours per day
        crew_size = 2.5  # Average crew size
        hours_per_day = 7  # Effective working hours
        
        # Calculate work days
        work_days = total_labor_hours / (crew_size * hours_per_day)
        
        # Add buffer for weather, permits, etc. (20%)
        work_days *= 1.2
        
        # Convert to weeks
        work_weeks = work_days / 5  # 5-day work week
        
        # Format timeline string
        if work_weeks < 1:
            return f"{int(work_days)} days"
        elif work_weeks < 4:
            return f"{int(work_weeks)} weeks"
        elif work_weeks < 12:
            months = int(work_weeks / 4)
            return f"{months}-{months+1} months"
        else:
            months = int(work_weeks / 4)
            return f"{months} months"
    
    def estimate_phased_approach(
        self,
        violations: List[Dict],
        budget_constraint: int
    ) -> Dict:
        """
        Estimate phased remediation approach based on budget constraints
        
        Args:
            violations: List of violations
            budget_constraint: Available budget
            
        Returns:
            Phased remediation plan
        """
        # Sort violations by priority
        sorted_violations = sorted(
            violations,
            key=lambda x: (x.get('priority', 3), -x.get('cost', 0))
        )
        
        phases = []
        current_phase = {
            'violations': [],
            'cost': 0,
            'phase_number': 1
        }
        
        remaining_budget = budget_constraint
        
        for violation in sorted_violations:
            cost = violation.get('cost', 0)
            
            if cost <= remaining_budget:
                current_phase['violations'].append(violation)
                current_phase['cost'] += cost
                remaining_budget -= cost
            else:
                # Start new phase
                if current_phase['violations']:
                    phases.append(current_phase)
                    current_phase = {
                        'violations': [violation],
                        'cost': cost,
                        'phase_number': len(phases) + 1
                    }
                    remaining_budget = budget_constraint - cost
        
        # Add last phase
        if current_phase['violations']:
            phases.append(current_phase)
        
        return {
            'phases': phases,
            'total_phases': len(phases),
            'fully_funded': remaining_budget >= 0
        }
    
    def generate_cost_summary(
        self,
        violations: List[Dict]
    ) -> Dict:
        """
        Generate comprehensive cost summary
        
        Args:
            violations: List of violations
            
        Returns:
            Detailed cost summary
        """
        estimate = self.estimate(violations)
        
        # Group by severity
        by_severity = {'High': 0, 'Medium': 0, 'Low': 0}
        for violation in violations:
            severity = violation.get('severity', 'Medium')
            cost = violation.get('cost', 0)
            by_severity[severity] += cost
        
        # Group by type
        by_type = {}
        for violation in violations:
            viol_type = violation['type']
            cost = violation.get('cost', 0)
            by_type[viol_type] = by_type.get(viol_type, 0) + cost
        
        # Calculate ROI metrics
        # Estimated annual cost of non-compliance (fines, liability)
        non_compliance_cost = len(violations) * 5000  # Conservative estimate
        
        return {
            'total_violations': len(violations),
            'total_cost': estimate['total_cost'],
            'total_with_contingency': estimate['total_with_contingency'],
            'timeline': estimate['timeline'],
            'by_severity': by_severity,
            'by_type': by_type,
            'labor_hours': estimate['labor_hours'],
            'non_compliance_risk': non_compliance_cost,
            'roi_payback_years': estimate['total_cost'] / max(non_compliance_cost, 1)
        }
