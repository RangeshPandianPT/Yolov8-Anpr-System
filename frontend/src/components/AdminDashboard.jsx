import { useState, useEffect } from 'react';
import './AdminDashboard.css';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

function AdminDashboard() {
  const [plates, setPlates] = useState([]);
  const [logs, setLogs] = useState([]);
  const [newPlate, setNewPlate] = useState('');
  const [newOwner, setNewOwner] = useState('');
  const [error, setError] = useState(null);

  const fetchPlates = async () => {
    try {
      const res = await fetch(`${API_BASE_URL}/api/plates`);
      const data = await res.json();
      setPlates(data);
    } catch (e) {
      console.error(e);
    }
  };

  const fetchLogs = async () => {
    try {
      const res = await fetch(`${API_BASE_URL}/api/logs`);
      const data = await res.json();
      setLogs(data);
    } catch (e) {
      console.error(e);
    }
  };

  useEffect(() => {
    fetchPlates();
    fetchLogs();
  }, []);

  const handleAddPlate = async (e) => {
    e.preventDefault();
    setError(null);
    try {
      const res = await fetch(`${API_BASE_URL}/api/plates`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ plate_number: newPlate, owner_name: newOwner })
      });
      if (!res.ok) throw new Error('Failed to add plate');
      setNewPlate('');
      setNewOwner('');
      fetchPlates();
    } catch (e) {
      setError(e.message);
    }
  };

  const handleDelete = async (id) => {
    try {
      await fetch(`${API_BASE_URL}/api/plates/${id}`, { method: 'DELETE' });
      fetchPlates();
    } catch (e) {
      console.error(e);
    }
  };

  return (
    <div className="admin-dashboard">
      <div className="admin-section">
        <h2>Authorized Plates</h2>
        <form onSubmit={handleAddPlate} className="add-plate-form">
          <input 
            type="text" 
            placeholder="Plate Number (e.g. MH12AB1234)" 
            value={newPlate} 
            onChange={(e) => setNewPlate(e.target.value)}
            required
          />
          <input 
            type="text" 
            placeholder="Owner Name" 
            value={newOwner} 
            onChange={(e) => setNewOwner(e.target.value)}
            required
          />
          <button type="submit">Add Plate</button>
        </form>
        {error && <p className="error-text">{error}</p>}
        
        <table className="admin-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Plate Number</th>
              <th>Owner Name</th>
              <th>Action</th>
            </tr>
          </thead>
          <tbody>
            {plates.map(p => (
              <tr key={p.id}>
                <td>{p.id}</td>
                <td>{p.plate_number}</td>
                <td>{p.owner_name}</td>
                <td><button onClick={() => handleDelete(p.id)} className="delete-btn">Remove</button></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="admin-section">
        <h2>Recent Access Logs</h2>
        <table className="admin-table">
          <thead>
            <tr>
              <th>Time</th>
              <th>Detected Plate</th>
              <th>Status</th>
              <th>Matched Plate</th>
            </tr>
          </thead>
          <tbody>
            {logs.map(log => (
              <tr key={log.id}>
                <td>{new Date(log.timestamp).toLocaleString()}</td>
                <td>{log.plate_number}</td>
                <td>
                  <span className={`status-badge-small ${log.is_authorized ? 'authorized' : 'denied'}`}>
                    {log.is_authorized ? 'Granted' : 'Denied'}
                  </span>
                </td>
                <td>{log.matched_plate || '-'}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default AdminDashboard;
