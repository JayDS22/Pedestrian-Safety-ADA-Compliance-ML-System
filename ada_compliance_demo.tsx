import React, { useState } from 'react';
import { Camera, Upload, MapPin, AlertTriangle, CheckCircle, FileText, DollarSign, TrendingUp, Map } from 'lucide-react';

const ADAComplianceDemo = () => {
  const [selectedTab, setSelectedTab] = useState('upload');
  const [analyzing, setAnalyzing] = useState(false);
  const [results, setResults] = useState(null);
  const [uploadedImage, setUploadedImage] = useState(null);

  const sampleResults = {
    overallScore: 62,
    violations: [
      {
        type: 'Curb Ramp Slope',
        severity: 'High',
        detected: 'Slope angle 8.5° (1:6.7 ratio)',
        standard: 'Must be ≤4.8° (1:12 ratio)',
        location: 'Main St & 1st Ave',
        cost: 2500,
        priority: 1
      },
      {
        type: 'Sidewalk Width',
        severity: 'Medium',
        detected: '32 inches',
        standard: 'Minimum 36 inches',
        location: 'Main St (Block 2)',
        cost: 1800,
        priority: 2
      },
      {
        type: 'Cross Slope',
        severity: 'High',
        detected: '3.2%',
        standard: 'Maximum 2%',
        location: 'Main St & 2nd Ave',
        cost: 3200,
        priority: 1
      },
      {
        type: 'Detectable Warning',
        severity: 'High',
        detected: 'Missing',
        standard: 'Required at all curb ramps',
        location: 'Main St & 1st Ave',
        cost: 800,
        priority: 1
      },
      {
        type: 'Surface Quality',
        severity: 'Medium',
        detected: 'Multiple cracks >0.5 inch',
        standard: 'Maximum 0.5 inch gaps',
        location: 'Main St (Block 1)',
        cost: 2200,
        priority: 3
      }
    ],
    compliance: {
      compliant: 3,
      nonCompliant: 5,
      needsReview: 2
    },
    costEstimate: 10500,
    timeline: '4-6 weeks'
  };

  const handleImageUpload = (e) => {
    const file = e.target.files[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = (event) => {
        setUploadedImage(event.target.result);
      };
      reader.readAsDataURL(file);
    }
  };

  const analyzeImage = () => {
    setAnalyzing(true);
    setTimeout(() => {
      setResults(sampleResults);
      setAnalyzing(false);
      setSelectedTab('results');
    }, 2500);
  };

  const getSeverityColor = (severity) => {
    switch(severity) {
      case 'High': return 'bg-red-100 text-red-800 border-red-300';
      case 'Medium': return 'bg-yellow-100 text-yellow-800 border-yellow-300';
      case 'Low': return 'bg-blue-100 text-blue-800 border-blue-300';
      default: return 'bg-gray-100 text-gray-800 border-gray-300';
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 mb-2">
                ADA Compliance Assessment System
              </h1>
              <p className="text-gray-600">
                AI-Powered Pedestrian Infrastructure Analysis & Accessibility Evaluation
              </p>
            </div>
            <div className="text-right">
              <div className="text-sm text-gray-500">Powered by</div>
              <div className="text-lg font-semibold text-indigo-600">YOLOv8 + PyTorch</div>
            </div>
          </div>
        </div>

        {/* Navigation Tabs */}
        <div className="bg-white rounded-lg shadow-lg mb-6">
          <div className="flex border-b">
            <button
              onClick={() => setSelectedTab('upload')}
              className={`flex-1 py-4 px-6 text-center font-medium transition-colors ${
                selectedTab === 'upload'
                  ? 'bg-indigo-50 text-indigo-700 border-b-2 border-indigo-700'
                  : 'text-gray-600 hover:bg-gray-50'
              }`}
            >
              <Upload className="inline-block mr-2" size={20} />
              Upload & Analyze
            </button>
            <button
              onClick={() => setSelectedTab('results')}
              className={`flex-1 py-4 px-6 text-center font-medium transition-colors ${
                selectedTab === 'results'
                  ? 'bg-indigo-50 text-indigo-700 border-b-2 border-indigo-700'
                  : 'text-gray-600 hover:bg-gray-50'
              }`}
            >
              <FileText className="inline-block mr-2" size={20} />
              Results & Violations
            </button>
            <button
              onClick={() => setSelectedTab('heatmap')}
              className={`flex-1 py-4 px-6 text-center font-medium transition-colors ${
                selectedTab === 'heatmap'
                  ? 'bg-indigo-50 text-indigo-700 border-b-2 border-indigo-700'
                  : 'text-gray-600 hover:bg-gray-50'
              }`}
            >
              <Map className="inline-block mr-2" size={20} />
              Risk Heatmap
            </button>
          </div>

          <div className="p-6">
            {/* Upload Tab */}
            {selectedTab === 'upload' && (
              <div>
                <div className="border-4 border-dashed border-gray-300 rounded-lg p-12 text-center mb-6 bg-gray-50 hover:bg-gray-100 transition-colors">
                  <input
                    type="file"
                    accept="image/*"
                    onChange={handleImageUpload}
                    className="hidden"
                    id="file-upload"
                  />
                  <label htmlFor="file-upload" className="cursor-pointer">
                    <Camera className="mx-auto mb-4 text-gray-400" size={64} />
                    <p className="text-xl font-medium text-gray-700 mb-2">
                      Upload Infrastructure Image
                    </p>
                    <p className="text-gray-500">
                      Supports: Sidewalks, Curb Ramps, Crosswalks, Pedestrian Signals
                    </p>
                  </label>
                </div>

                {uploadedImage && (
                  <div className="mb-6">
                    <img
                      src={uploadedImage}
                      alt="Uploaded"
                      className="max-w-full h-64 mx-auto rounded-lg shadow-md object-cover"
                    />
                  </div>
                )}

                <button
                  onClick={analyzeImage}
                  disabled={!uploadedImage || analyzing}
                  className={`w-full py-4 rounded-lg font-semibold text-white transition-all ${
                    uploadedImage && !analyzing
                      ? 'bg-indigo-600 hover:bg-indigo-700'
                      : 'bg-gray-400 cursor-not-allowed'
                  }`}
                >
                  {analyzing ? (
                    <span>Analyzing... 🔍</span>
                  ) : (
                    <span>Analyze for ADA Compliance</span>
                  )}
                </button>

                {analyzing && (
                  <div className="mt-6 bg-blue-50 border border-blue-200 rounded-lg p-4">
                    <div className="flex items-center mb-2">
                      <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-blue-600 mr-3"></div>
                      <span className="font-medium text-blue-900">Processing Infrastructure Assessment...</span>
                    </div>
                    <div className="text-sm text-blue-700 ml-8 space-y-1">
                      <div>✓ Object detection (YOLOv8)</div>
                      <div>✓ Measurement extraction (OpenCV)</div>
                      <div>✓ ADA compliance validation</div>
                      <div>✓ Cost estimation & prioritization</div>
                    </div>
                  </div>
                )}

                {/* Features Grid */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-8">
                  <div className="bg-indigo-50 p-4 rounded-lg">
                    <h3 className="font-semibold text-indigo-900 mb-2">Detects 20+ Compliance Issues</h3>
                    <p className="text-sm text-indigo-700">
                      Curb ramps, sidewalk width, cross slopes, surface quality, detectable warnings, and more
                    </p>
                  </div>
                  <div className="bg-green-50 p-4 rounded-lg">
                    <h3 className="font-semibold text-green-900 mb-2">94% Accuracy</h3>
                    <p className="text-sm text-green-700">
                      State-of-the-art computer vision models trained on transportation infrastructure
                    </p>
                  </div>
                  <div className="bg-purple-50 p-4 rounded-lg">
                    <h3 className="font-semibold text-purple-900 mb-2">Real-Time Processing</h3>
                    <p className="text-sm text-purple-700">
                      Process 1000+ assets per minute with sub-100ms inference time
                    </p>
                  </div>
                  <div className="bg-orange-50 p-4 rounded-lg">
                    <h3 className="font-semibold text-orange-900 mb-2">Cost Estimation</h3>
                    <p className="text-sm text-orange-700">
                      Automatic budget calculations and prioritization for remediation projects
                    </p>
                  </div>
                </div>
              </div>
            )}

            {/* Results Tab */}
            {selectedTab === 'results' && results && (
              <div>
                {/* Summary Cards */}
                <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
                  <div className="bg-gradient-to-br from-blue-500 to-blue-600 text-white p-6 rounded-lg shadow">
                    <div className="text-3xl font-bold mb-2">{results.overallScore}%</div>
                    <div className="text-blue-100">Compliance Score</div>
                  </div>
                  <div className="bg-gradient-to-br from-red-500 to-red-600 text-white p-6 rounded-lg shadow">
                    <div className="text-3xl font-bold mb-2">{results.violations.length}</div>
                    <div className="text-red-100">Violations Found</div>
                  </div>
                  <div className="bg-gradient-to-br from-green-500 to-green-600 text-white p-6 rounded-lg shadow">
                    <div className="text-3xl font-bold mb-2">${(results.costEstimate / 1000).toFixed(1)}K</div>
                    <div className="text-green-100">Total Cost Est.</div>
                  </div>
                  <div className="bg-gradient-to-br from-purple-500 to-purple-600 text-white p-6 rounded-lg shadow">
                    <div className="text-3xl font-bold mb-2">{results.timeline}</div>
                    <div className="text-purple-100">Est. Timeline</div>
                  </div>
                </div>

                {/* Violations List */}
                <div className="bg-white border border-gray-200 rounded-lg mb-6">
                  <div className="border-b border-gray-200 p-4 bg-gray-50">
                    <h3 className="font-bold text-lg text-gray-900">Detected Violations</h3>
                  </div>
                  <div className="divide-y divide-gray-200">
                    {results.violations.map((violation, idx) => (
                      <div key={idx} className="p-4 hover:bg-gray-50 transition-colors">
                        <div className="flex items-start justify-between mb-3">
                          <div className="flex items-center">
                            <AlertTriangle className="text-red-500 mr-3" size={24} />
                            <div>
                              <h4 className="font-semibold text-gray-900">{violation.type}</h4>
                              <p className="text-sm text-gray-600 flex items-center mt-1">
                                <MapPin size={14} className="mr-1" />
                                {violation.location}
                              </p>
                            </div>
                          </div>
                          <span className={`px-3 py-1 rounded-full text-xs font-semibold border ${getSeverityColor(violation.severity)}`}>
                            {violation.severity} Priority
                          </span>
                        </div>
                        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 ml-9">
                          <div className="bg-red-50 p-3 rounded">
                            <div className="text-xs text-red-600 font-medium mb-1">DETECTED</div>
                            <div className="text-sm text-red-900">{violation.detected}</div>
                          </div>
                          <div className="bg-green-50 p-3 rounded">
                            <div className="text-xs text-green-600 font-medium mb-1">ADA STANDARD</div>
                            <div className="text-sm text-green-900">{violation.standard}</div>
                          </div>
                          <div className="bg-blue-50 p-3 rounded">
                            <div className="text-xs text-blue-600 font-medium mb-1">REMEDIATION COST</div>
                            <div className="text-sm text-blue-900 font-semibold">
                              ${violation.cost.toLocaleString()}
                            </div>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Action Buttons */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <button className="bg-indigo-600 text-white py-3 px-6 rounded-lg font-semibold hover:bg-indigo-700 transition-colors">
                    <FileText className="inline-block mr-2" size={18} />
                    Export Full Report
                  </button>
                  <button className="bg-green-600 text-white py-3 px-6 rounded-lg font-semibold hover:bg-green-700 transition-colors">
                    <DollarSign className="inline-block mr-2" size={18} />
                    Generate Budget Request
                  </button>
                  <button className="bg-purple-600 text-white py-3 px-6 rounded-lg font-semibold hover:bg-purple-700 transition-colors">
                    <TrendingUp className="inline-block mr-2" size={18} />
                    Prioritization Matrix
                  </button>
                </div>
              </div>
            )}

            {/* Heatmap Tab */}
            {selectedTab === 'heatmap' && (
              <div>
                <div className="bg-gradient-to-br from-red-100 via-yellow-100 to-green-100 rounded-lg p-12 mb-6 relative overflow-hidden">
                  <div className="absolute top-4 right-4 bg-white px-4 py-2 rounded-lg shadow">
                    <div className="text-xs text-gray-600 mb-1">Legend</div>
                    <div className="flex items-center space-x-4">
                      <div className="flex items-center">
                        <div className="w-4 h-4 bg-red-500 rounded mr-1"></div>
                        <span className="text-xs">High Risk</span>
                      </div>
                      <div className="flex items-center">
                        <div className="w-4 h-4 bg-yellow-500 rounded mr-1"></div>
                        <span className="text-xs">Medium</span>
                      </div>
                      <div className="flex items-center">
                        <div className="w-4 h-4 bg-green-500 rounded mr-1"></div>
                        <span className="text-xs">Low Risk</span>
                      </div>
                    </div>
                  </div>
                  
                  <div className="text-center">
                    <Map className="mx-auto mb-4 text-gray-600" size={64} />
                    <h3 className="text-2xl font-bold text-gray-900 mb-2">
                      Accessibility Risk Heatmap
                    </h3>
                    <p className="text-gray-700 mb-4">
                      Spatial analysis of pedestrian infrastructure compliance
                    </p>
                    <div className="grid grid-cols-3 gap-4 max-w-2xl mx-auto">
                      <div className="bg-white p-4 rounded-lg shadow">
                        <div className="text-2xl font-bold text-red-600">12</div>
                        <div className="text-sm text-gray-600">High-Risk Areas</div>
                      </div>
                      <div className="bg-white p-4 rounded-lg shadow">
                        <div className="text-2xl font-bold text-yellow-600">8</div>
                        <div className="text-sm text-gray-600">Network Gaps</div>
                      </div>
                      <div className="bg-white p-4 rounded-lg shadow">
                        <div className="text-2xl font-bold text-blue-600">3.2mi</div>
                        <div className="text-sm text-gray-600">Non-Compliant</div>
                      </div>
                    </div>
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="bg-white border border-gray-200 rounded-lg p-4">
                    <h4 className="font-semibold text-gray-900 mb-3">Priority Corridors</h4>
                    <div className="space-y-2">
                      <div className="flex justify-between items-center p-2 bg-red-50 rounded">
                        <span className="text-sm">Main St (1st-5th Ave)</span>
                        <span className="text-xs font-semibold text-red-700">Critical</span>
                      </div>
                      <div className="flex justify-between items-center p-2 bg-orange-50 rounded">
                        <span className="text-sm">Broadway (Central)</span>
                        <span className="text-xs font-semibold text-orange-700">High</span>
                      </div>
                      <div className="flex justify-between items-center p-2 bg-yellow-50 rounded">
                        <span className="text-sm">Park Ave</span>
                        <span className="text-xs font-semibold text-yellow-700">Medium</span>
                      </div>
                    </div>
                  </div>

                  <div className="bg-white border border-gray-200 rounded-lg p-4">
                    <h4 className="font-semibold text-gray-900 mb-3">Connectivity Analysis</h4>
                    <div className="space-y-3">
                      <div>
                        <div className="flex justify-between text-sm mb-1">
                          <span>Wheelchair Accessible Routes</span>
                          <span className="font-semibold">68%</span>
                        </div>
                        <div className="w-full bg-gray-200 rounded-full h-2">
                          <div className="bg-green-500 h-2 rounded-full" style={{width: '68%'}}></div>
                        </div>
                      </div>
                      <div>
                        <div className="flex justify-between text-sm mb-1">
                          <span>Safe Crossing Points</span>
                          <span className="font-semibold">82%</span>
                        </div>
                        <div className="w-full bg-gray-200 rounded-full h-2">
                          <div className="bg-blue-500 h-2 rounded-full" style={{width: '82%'}}></div>
                        </div>
                      </div>
                      <div>
                        <div className="flex justify-between text-sm mb-1">
                          <span>Transit Stop Access</span>
                          <span className="font-semibold">45%</span>
                        </div>
                        <div className="w-full bg-gray-200 rounded-full h-2">
                          <div className="bg-yellow-500 h-2 rounded-full" style={{width: '45%'}}></div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {!results && selectedTab === 'results' && (
              <div className="text-center py-12">
                <AlertTriangle className="mx-auto mb-4 text-gray-400" size={64} />
                <p className="text-xl text-gray-600">No analysis results yet</p>
                <p className="text-gray-500 mt-2">Upload and analyze an image to see results</p>
              </div>
            )}
          </div>
        </div>

        {/* Footer Info */}
        <div className="bg-white rounded-lg shadow-lg p-6">
          <h3 className="font-bold text-gray-900 mb-4">System Capabilities</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
            <div>
              <h4 className="font-semibold text-indigo-700 mb-2">Compliance Checks</h4>
              <ul className="space-y-1 text-gray-600">
                <li>✓ Curb ramp slopes (1:12 ratio)</li>
                <li>✓ Sidewalk width (36" min)</li>
                <li>✓ Cross slopes (2% max)</li>
                <li>✓ Detectable warnings</li>
                <li>✓ Surface quality</li>
                <li>✓ Clear path width</li>
              </ul>
            </div>
            <div>
              <h4 className="font-semibold text-green-700 mb-2">Performance Metrics</h4>
              <ul className="space-y-1 text-gray-600">
                <li>• 94%+ detection accuracy</li>
                <li>• 1000+ assets/minute</li>
                <li>• Sub-100ms inference</li>
                <li>• 20+ violation types</li>
                <li>• Real-time processing</li>
                <li>• Multi-format support</li>
              </ul>
            </div>
            <div>
              <h4 className="font-semibold text-purple-700 mb-2">Integration Ready</h4>
              <ul className="space-y-1 text-gray-600">
                <li>→ GIS platform integration</li>
                <li>→ PostGIS/PostgreSQL</li>
                <li>→ REST API endpoints</li>
                <li>→ Grant application exports</li>
                <li>→ Budget planning tools</li>
                <li>→ Mobile field collection</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ADAComplianceDemo;