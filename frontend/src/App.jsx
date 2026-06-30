import { useState } from 'react';
import Dropzone from './components/Dropzone';
import AdminDashboard from './components/AdminDashboard';
import VideoScan from './components/VideoScan';
import './App.css';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

function App() {
  const [activeTab, setActiveTab] = useState('image'); // 'image', 'video', 'admin'
  const [selectedFile, setSelectedFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const handleFileSelect = (file) => {
    setSelectedFile(file);
    const objectUrl = URL.createObjectURL(file);
    setPreview(objectUrl);
    setResult(null);
    setError(null);
  };

  const processImage = async () => {
    if (!selectedFile) return;

    setLoading(true);
    setError(null);

    const formData = new FormData();
    formData.append('file', selectedFile);

    try {
      const response = await fetch(`${API_BASE_URL}/api/verify`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`Server returned ${response.status}`);
      }

      const data = await response.json();
      
      if (data.status === 'error') {
        throw new Error(data.message || 'Error processing image');
      }

      setResult(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const reset = () => {
    setSelectedFile(null);
    setPreview(null);
    setResult(null);
    setError(null);
  };

  return (
    <div className="glass-container" style={activeTab === 'admin' ? {maxWidth: '800px'} : {}}>
      <header>
        <h1>Next-Gen ANPR</h1>
        <p className="subtitle">Automatic Number Plate Recognition & Verification</p>
      </header>

      <div className="tabs">
        <button 
          className={activeTab === 'image' ? 'active' : ''} 
          onClick={() => setActiveTab('image')}
        >Image Scan</button>
        <button 
          className={activeTab === 'video' ? 'active' : ''} 
          onClick={() => setActiveTab('video')}
        >Video Scan</button>
        <button 
          className={activeTab === 'admin' ? 'active' : ''} 
          onClick={() => setActiveTab('admin')}
        >Admin Dashboard</button>
      </div>

      <main>
        {activeTab === 'image' && (
          !preview ? (
            <Dropzone onFileSelect={handleFileSelect} />
          ) : (
            <div className="preview-container">
              <div className="image-preview-wrapper">
                <img src={preview} alt="Selected vehicle" className="image-preview" />
                <button className="change-btn" onClick={reset}>✕</button>
              </div>
              
              {!result && !loading && !error && (
                <button className="process-btn" onClick={processImage}>
                  Analyze Image
                </button>
              )}

              {loading && (
                <div className="loading-state">
                  <div className="loader-spinner"></div>
                  <p>Analyzing Vehicle Data...</p>
                </div>
              )}

              {error && (
                <div className="error-card">
                  <div className="icon">⚠️</div>
                  <p>{error}</p>
                  <button className="retry-btn" onClick={reset}>Try Again</button>
                </div>
              )}

              {result && (
                <div className="result-card fade-in">
                  <div className="result-header">
                    <h3>Analysis Complete</h3>
                    <span className="time">{result.processing_time_sec}s</span>
                  </div>
                  
                  <div className="plate-display">
                    <span className="plate-label">Detected Plate</span>
                    <div className="plate-number">{result.predicted_plate}</div>
                  </div>

                  <div className={`status-badge ${result.is_authorized ? 'authorized' : 'denied'}`}>
                    {result.is_authorized ? (
                      <>
                        <span className="status-icon">✅</span>
                        <span>Access Granted</span>
                      </>
                    ) : (
                      <>
                        <span className="status-icon">❌</span>
                        <span>Access Denied</span>
                      </>
                    )}
                  </div>

                  {result.is_authorized && result.best_match_db && (
                    <p className="db-match">Matched with database record: <strong>{result.best_match_db}</strong></p>
                  )}
                  
                  <button className="new-scan-btn" onClick={reset}>Scan New Vehicle</button>
                </div>
              )}
            </div>
          )
        )}

        {activeTab === 'video' && <VideoScan />}
        
        {activeTab === 'admin' && <AdminDashboard />}

      </main>
    </div>
  );
}

export default App;
