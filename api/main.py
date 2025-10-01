"""
FastAPI REST API for ADA Compliance Assessment System
"""

from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import cv2
import numpy as np
from pathlib import Path
import logging
from datetime import datetime

from ada_compliance.analyzer import ComplianceAnalyzer
from ada_compliance.report_generator import ReportGenerator

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="ADA Compliance Assessment API",
    description="AI-powered pedestrian infrastructure assessment",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
analyzer = ComplianceAnalyzer()
report_gen = ReportGenerator()

# Pydantic models
class AnalysisResponse(BaseModel):
    compliance_score: int
    total_violations: int
    total_cost: int
    estimated_timeline: str
    violations: List[dict]
    timestamp: str

class HealthCheck(BaseModel):
    status: str
    version: str
    timestamp: str


@app.get("/", response_model=HealthCheck)
async def root():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    }


@app.post("/api/v1/analyze", response_model=AnalysisResponse)
async def analyze_image(
    file: UploadFile = File(...),
    location: Optional[str] = Form(None),
    confidence_threshold: Optional[float] = Form(0.6),
    generate_report: Optional[bool] = Form(False)
):
    """
    Analyze uploaded image for ADA compliance
    
    Args:
        file: Image file (JPG, PNG)
        location: Optional location description
        confidence_threshold: Detection confidence threshold
        generate_report: Whether to generate PDF report
        
    Returns:
        Analysis results with violations and compliance score
    """
    try:
        # Read and decode image
        contents = await file.read()
        nparr = np.frombuffer(contents, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if image is None:
            raise HTTPException(status_code=400, detail="Invalid image file")
        
        # Run analysis
        logger.info(f"Analyzing image: {file.filename}, location: {location}")
        results = analyzer.analyze(
            image,
            confidence_threshold=confidence_threshold,
            location=location
        )
        
        # Generate report if requested
        if generate_report:
            report_path = report_gen.generate_pdf(results)
            results['report_path'] = report_path
        
        # Prepare response (remove non-serializable items)
        response = {
            'compliance_score': results['compliance_score'],
            'total_violations': len(results['violations']),
            'total_cost': results['total_cost'],
            'estimated_timeline': results['estimated_timeline'],
            'violations': results['violations'],
            'timestamp': results['timestamp']
        }
        
        logger.info(f"Analysis complete: {len(results['violations'])} violations found")
        return response
        
    except Exception as e:
        logger.error(f"Error analyzing image: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/batch-analyze")
async def batch_analyze(
    files: List[UploadFile] = File(...)
):
    """
    Analyze multiple images in batch
    
    Args:
        files: List of image files
        
    Returns:
        List of analysis results
    """
    try:
        results = []
        
        for file in files:
            contents = await file.read()
            nparr = np.frombuffer(contents, np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if image is not None:
                result = analyzer.analyze(image)
                result['filename'] = file.filename
                # Remove non-serializable items
                result.pop('annotated_image', None)
                results.append(result)
        
        logger.info(f"Batch analysis complete: {len(results)} images processed")
        return JSONResponse(content={"results": results})
        
    except Exception as e:
        logger.error(f"Error in batch analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/statistics")
async def get_statistics(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
):
    """
    Get compliance statistics
    
    Args:
        start_date: Start date filter (ISO format)
        end_date: End date filter (ISO format)
        
    Returns:
        Statistical summary
    """
    # In production, this would query database
    # For demo, return mock statistics
    return {
        "total_assessments": 1247,
        "average_compliance_score": 72.3,
        "total_violations": 3891,
        "total_estimated_cost": 8234000,
        "common_violations": {
            "Curb Ramp Slope": 456,
            "Sidewalk Width": 392,
            "Cross Slope": 348,
            "Surface Quality": 287,
            "Detectable Warning": 245
        },
        "average_processing_time_ms": 73
    }


@app.post("/api/v1/generate-report")
async def generate_report(
    results: dict
):
    """
    Generate PDF report from analysis results
    
    Args:
        results: Analysis results dictionary
        
    Returns:
        PDF file
    """
    try:
        report_path = report_gen.generate_pdf(results)
        return FileResponse(
            report_path,
            media_type='application/pdf',
            filename=Path(report_path).name
        )
    except Exception as e:
        logger.error(f"Error generating report: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/export-csv")
async def export_csv(
    results: dict
):
    """
    Export violations to CSV
    
    Args:
        results: Analysis results dictionary
        
    Returns:
        CSV file
    """
    try:
        csv_path = report_gen.export_csv(results)
        return FileResponse(
            csv_path,
            media_type='text/csv',
            filename=Path(csv_path).name
        )
    except Exception as e:
        logger.error(f"Error exporting CSV: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/export-geojson")
async def export_geojson(
    results: dict
):
    """
    Export violations to GeoJSON for GIS integration
    
    Args:
        results: Analysis results dictionary
        
    Returns:
        GeoJSON file
    """
    try:
        geojson_path = report_gen.export_geojson(results)
        return FileResponse(
            geojson_path,
            media_type='application/geo+json',
            filename=Path(geojson_path).name
        )
    except Exception as e:
        logger.error(f"Error exporting GeoJSON: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "components": {
            "analyzer": "operational",
            "report_generator": "operational",
            "database": "operational"
        },
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
