import React, { useState } from 'react';
import axios from 'axios';
import { ShieldAlert, Mail, History, BarChart3, Send, Zap, ShieldCheck } from 'lucide-react';
import './App.css';

const App = () => {
  const [content, setContent] = useState("");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleScan = async () => {
    if (!content) return;
    setLoading(true);
    try {
      const response = await axios.post('http://127.0.0.1:5000/api/analyze', { text: content });
      setResult(response.data);
    } catch (err) {
      console.log(err);
      alert("Backend error! Make sure Flask is running on port 5000");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="dashboard-container">
      {/* SIDEBAR */}
      <aside className="sidebar">
        <div className="logo">
          <div className="logo-icon"><ShieldAlert size={20} /></div>
          <span>SpamGuard AI</span>
        </div>

        <div className="nav-links">
          <div className="nav-item active"><Mail size={18} /> Analyzer</div>
          <div className="nav-item"><History size={18} /> History</div>
          <div className="nav-item"><BarChart3 size={18} /> Analytics</div>
        </div>
      </aside>

      {/* MAIN */}
      <main className="main-content">
        <header>
          <h1>Email Intelligence</h1>
          <p>Scan incoming messages for spam patterns and malicious NLP signatures.</p>
        </header>

        <section className="scan-card">
          <div className="input-header">
            <span>RAW EMAIL CONTENT</span>
            <span>SECURE SCAN ACTIVE</span>
          </div>
          <textarea 
            placeholder="Paste raw email content here..."
            value={content}
            onChange={(e) => setContent(e.target.value)}
          />
          <div className="action-bar">
            <button className="btn-primary" onClick={handleScan} disabled={loading || !content}>
              {loading ? <Zap size={18} /> : <Send size={18} />}
              {loading ? "Analyzing..." : "Run ML Scan"}
            </button>
          </div>
        </section>

        {result && (
          <div className="results-grid">
            <div className="result-item">
              <div className="status-label">Final Verdict</div>
              <div className={`status-value ${result.label === 'Spam/Negative' ? 'spam' : 'ham'}`}>
                {result.label === 'Spam/Negative' ? 'SPAM DETECTED' : 'SECURE / HAM'}
              </div>
            </div>
            <div className="result-item">
              <div className="status-label">ML Confidence</div>
              <div className="status-value">{Math.abs(result.score * 100).toFixed(1)}%</div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
};

export default App;