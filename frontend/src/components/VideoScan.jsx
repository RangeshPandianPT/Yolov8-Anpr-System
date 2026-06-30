import { useState, useRef } from 'react';
import './VideoScan.css';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

function VideoScan() {
  const [selectedFile, setSelectedFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  
  const fileInputRef = useRef(null);

  const handleFileSelect = (e) => {
    const file = e.target.files[0];
    if (file && file.type.startsWith('video/')) {
      setSelectedFile(file);
      setResult(null);
      setError(null);
    } else {
      setError('Please select a valid video file (.mp4, .mov, etc)');
    }
  };

  const processVideo = async () => {
    if (!selectedFile) return;

    setLoading(true);
    setError(null);

    const formData = new FormData();
    formData.append('file', selectedFile);

    try {
      const response = await fetch(`${API_BASE_URL}/api/verify/video`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`Server returned ${response.status}`);
      }

      const data = await response.json();
      
      if (data.status === 'error') {
        throw new Error(data.message || 'Error processing video');
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
    setResult(null);
    setError(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  return (
    <div className="video-scan-container">
      {!result ? (
        <div className="upload-section">
          <input 
            type="file" 
            accept="video/*" 
            onChange={handleFileSelect} 
            ref={fileInputRef}
            style={{display: 'none'}}
            id="video-upload"
          />
          <label htmlFor="video-upload" className="upload-label">
            <div className="icon">🎥</div>
            <span>{selectedFile ? selectedFile.name : 'Click to upload a video file'}</span>
          </label>
          
          {selectedFile && !loading && (
            <button className="process-btn" onClick={processVideo}>Analyze Video</button>
          )}

          {loading && (
            <div className="loading-state">
              <div className="loader-spinner"></div>
              <p>Analyzing Video... This may take a moment.</p>
            </div>
          )}

          {error && <p className="error-text">{error}</p>}
        </div>
      ) : (
        <div className="result-section">
          <h3>Video Analysis Complete</h3>
          <p>Processing Time: {result.processing_time_sec}s</p>
          
          <h4>Unique Plates Detected:</h4>
          {result.unique_plates && result.unique_plates.length > 0 ? (
            <div className="plates-grid">
              {result.unique_plates.map((plate, idx) => (
                <div key={idx} className="plate-card">
                  <div className="plate-number">{plate.predicted_plate}</div>
                  <div className={`status-badge-small ${plate.is_authorized ? 'authorized' : 'denied'}`}>
                    {plate.is_authorized ? 'Authorized' : 'Denied'}
                  </div>
                  {plate.best_match_db && <div className="match">Matched: {plate.best_match_db}</div>}
                </div>
              ))}
            </div>
          ) : (
            <p>No valid plates found in the video.</p>
          )}

          <button className="new-scan-btn" onClick={reset}>Scan Another Video</button>
        </div>
      )}
    </div>
  );
}

export default VideoScan;
