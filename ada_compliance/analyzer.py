"""
ADA Compliance Analyzer - Core detection and analysis engine
"""

import cv2
import numpy as np
from pathlib import Path
import torch
from ultralytics import YOLO
from typing import Dict, List, Tuple, Optional
import logging

from .compliance_engine import ComplianceRuleEngine
from .cost_estimator import CostEstimator
from .measurement_extractor import MeasurementExtractor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ComplianceAnalyzer:
    """
    Main analyzer class for ADA compliance assessment
    Integrates YOLOv8 detection, measurement extraction, and compliance evaluation
    """
    
    def __init__(
        self,
        model_path: str = "models/yolov8x-ada.pt",
        confidence_threshold: float = 0.6,
        device: str = "auto"
    ):
        """
        Initialize the analyzer
        
        Args:
            model_path: Path to trained YOLOv8 model
            confidence_threshold: Minimum confidence for detections
            device: Device to run inference ('cpu', 'cuda', 'auto')
        """
        self.confidence_threshold = confidence_threshold
        self.device = self._get_device(device)
        
        # Initialize components
        self.model = self._load_model(model_path)
        self.compliance_engine = ComplianceRuleEngine()
        self.cost_estimator = CostEstimator()
        self.measurement_extractor = MeasurementExtractor()
        
        logger.info(f"Analyzer initialized on device: {self.device}")
    
    def _get_device(self, device: str) -> str:
        """Determine which device to use"""
        if device == "auto":
            return "cuda" if torch.cuda.is_available() else "cpu"
        return device
    
    def _load_model(self, model_path: str) -> YOLO:
        """Load YOLOv8 model"""
        try:
            if Path(model_path).exists():
                model = YOLO(model_path)
                logger.info(f"Loaded custom model from {model_path}")
            else:
                # Use pretrained YOLOv8 as fallback
                model = YOLO('yolov8x.pt')
                logger.warning(f"Model not found at {model_path}, using pretrained YOLOv8x")
            
            return model
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            raise
    
    def analyze(
        self,
        image: np.ndarray,
        confidence_threshold: Optional[float] = None,
        location: Optional[str] = None
    ) -> Dict:
        """
        Analyze image for ADA compliance
        
        Args:
            image: Input image as numpy array (BGR format)
            confidence_threshold: Override default confidence threshold
            location: Optional location string for the asset
            
        Returns:
            Dictionary containing analysis results
        """
        conf_threshold = confidence_threshold or self.confidence_threshold
        
        # Run object detection
        detections = self._detect_objects(image, conf_threshold)
        
        # Extract measurements from detected objects
        measurements = self.measurement_extractor.extract(image, detections)
        
        # Evaluate ADA compliance
        violations = self.compliance_engine.evaluate(measurements, detections)
        
        # Calculate compliance score
        compliance_score = self._calculate_compliance_score(violations, detections)
        
        # Estimate costs and timeline
        cost_analysis = self.cost_estimator.estimate(violations)
        
        # Generate annotated image
        annotated_image = self._annotate_image(image, detections, violations)
        
        # Compile results
        results = {
            'compliance_score': compliance_score,
            'violations': violations,
            'detections': detections,
            'measurements': measurements,
            'total_cost': cost_analysis['total_cost'],
            'estimated_timeline': cost_analysis['timeline'],
            'cost_breakdown': cost_analysis['breakdown'],
            'annotated_image': annotated_image,
            'location': location,
            'timestamp': self._get_timestamp()
        }
        
        logger.info(f"Analysis complete: {len(violations)} violations found, "
                   f"score: {compliance_score}%")
        
        return results
    
    def _detect_objects(
        self,
        image: np.ndarray,
        confidence_threshold: float
    ) -> List[Dict]:
        """
        Run YOLOv8 object detection
        
        Args:
            image: Input image
            confidence_threshold: Minimum confidence for detections
            
        Returns:
            List of detected objects with bounding boxes and classes
        """
        # Run inference
        results = self.model(image, conf=confidence_threshold, device=self.device)
        
        detections = []
        for result in results:
            boxes = result.boxes
            for i, box in enumerate(boxes):
                detection = {
                    'class_id': int(box.cls[0]),
                    'class_name': result.names[int(box.cls[0])],
                    'confidence': float(box.conf[0]),
                    'bbox': box.xyxy[0].cpu().numpy().tolist(),
                    'center': self._calculate_center(box.xyxy[0].cpu().numpy())
                }
                detections.append(detection)
        
        return detections
    
    def _calculate_center(self, bbox: np.ndarray) -> Tuple[float, float]:
        """Calculate center point of bounding box"""
        x1, y1, x2, y2 = bbox
        return ((x1 + x2) / 2, (y1 + y2) / 2)
    
    def _calculate_compliance_score(
        self,
        violations: List[Dict],
        detections: List[Dict]
    ) -> int:
        """
        Calculate overall compliance score (0-100)
        
        Higher scores indicate better compliance
        """
        if not detections:
            return 100
        
        # Weight violations by severity
        severity_weights = {'High': 3, 'Medium': 2, 'Low': 1}
        
        total_weight = sum(severity_weights[v['severity']] for v in violations)
        max_possible_weight = len(detections) * 3  # Assume all could be High
        
        if max_possible_weight == 0:
            return 100
        
        # Calculate score (inverse of violation weight)
        score = 100 - int((total_weight / max_possible_weight) * 100)
        return max(0, min(100, score))
    
    def _annotate_image(
        self,
        image: np.ndarray,
        detections: List[Dict],
        violations: List[Dict]
    ) -> np.ndarray:
        """
        Draw annotations on image showing detections and violations
        
        Args:
            image: Original image
            detections: List of detected objects
            violations: List of ADA violations
            
        Returns:
            Annotated image
        """
        annotated = image.copy()
        
        # Color scheme for severity
        severity_colors = {
            'High': (0, 0, 255),      # Red
            'Medium': (0, 165, 255),  # Orange
            'Low': (0, 255, 255)      # Yellow
        }
        
        # Draw detections
        for detection in detections:
            x1, y1, x2, y2 = map(int, detection['bbox'])
            
            # Default green for compliant items
            color = (0, 255, 0)
            thickness = 2
            
            # Check if this detection has violations
            for violation in violations:
                if self._is_related(detection, violation):
                    color = severity_colors[violation['severity']]
                    thickness = 3
                    break
            
            # Draw bounding box
            cv2.rectangle(annotated, (x1, y1), (x2, y2), color, thickness)
            
            # Draw label
            label = f"{detection['class_name']} {detection['confidence']:.2f}"
            cv2.putText(
                annotated,
                label,
                (x1, y1 - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                color,
                2
            )
        
        # Draw violation markers
        for violation in violations:
            if 'bbox' in violation:
                x1, y1, x2, y2 = map(int, violation['bbox'])
                center_x = (x1 + x2) // 2
                center_y = (y1 + y2) // 2
                
                # Draw warning icon
                color = severity_colors[violation['severity']]
                cv2.circle(annotated, (center_x, center_y), 15, color, -1)
                cv2.putText(
                    annotated,
                    "!",
                    (center_x - 5, center_y + 8),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.8,
                    (255, 255, 255),
                    2
                )
        
        return annotated
    
    def _is_related(self, detection: Dict, violation: Dict) -> bool:
        """Check if a detection is related to a violation"""
        # Simple check based on class type
        violation_type = violation['type'].lower()
        detection_class = detection['class_name'].lower()
        
        # Mapping of violation types to detection classes
        type_mapping = {
            'curb_ramp': ['curb', 'ramp'],
            'sidewalk': ['sidewalk', 'path'],
            'crosswalk': ['crosswalk', 'crossing'],
            'surface': ['sidewalk', 'path', 'ramp']
        }
        
        for viol_key, detect_keywords in type_mapping.items():
            if viol_key in violation_type:
                return any(keyword in detection_class for keyword in detect_keywords)
        
        return False
    
    def _get_timestamp(self) -> str:
        """Get current timestamp"""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def analyze_batch(
        self,
        image_paths: List[str],
        output_dir: Optional[str] = None
    ) -> List[Dict]:
        """
        Analyze multiple images in batch
        
        Args:
            image_paths: List of paths to images
            output_dir: Optional directory to save results
            
        Returns:
            List of analysis results for each image
        """
        results = []
        
        for img_path in image_paths:
            try:
                # Read image
                image = cv2.imread(str(img_path))
                if image is None:
                    logger.warning(f"Could not read image: {img_path}")
                    continue
                
                # Analyze
                result = self.analyze(image)
                result['image_path'] = str(img_path)
                results.append(result)
                
                logger.info(f"Processed: {img_path}")
                
            except Exception as e:
                logger.error(f"Error processing {img_path}: {e}")
                continue
        
        # Save results if output directory specified
        if output_dir:
            self._save_batch_results(results, output_dir)
        
        return results
    
    def _save_batch_results(self, results: List[Dict], output_dir: str):
        """Save batch analysis results"""
        import json
        from datetime import datetime
        
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        results_file = output_path / f"batch_results_{timestamp}.json"
        
        # Remove non-serializable items
        serializable_results = []
        for result in results:
            clean_result = {k: v for k, v in result.items() 
                          if k != 'annotated_image'}
            serializable_results.append(clean_result)
        
        with open(results_file, 'w') as f:
            json.dump(serializable_results, f, indent=2)
        
        logger.info(f"Batch results saved to: {results_file}")
