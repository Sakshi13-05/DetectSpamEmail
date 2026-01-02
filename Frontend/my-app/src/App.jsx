import React, { useState } from 'react';
import axios from 'axios';
import { ShieldAlert, Mail, History, BarChart3, Send, Zap } from 'lucide-react';
import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer } from 'recharts';
import './App.css';

const App = () => {
  const [content, setContent] = useState("");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState("analyzer");
  const [history, setHistory] = useState([]);
  const [analytics, setAnalytics] = useState([]);

  const handleScan = async () => {
    if (!content) return;
    setLoading(true);
    try {
      const response = await axios.post('http://127.0.0.1:5000/api/analyze', { text: content });
      setResult(response.data);
    } catch (err) {
      console.log(err)
      alert("Backend error! Make sure Flask is running on port 5000");
    } finally {
      setLoading(false);
    }
  };

  const switchTab = async (tab) => {
    setActiveTab(tab);
    if (tab === "history") {
      const res = await axios.get('http://127.0.0.1:5000/api/history');
      setHistory(res.data);
    } else if (tab === "analytics") {
      const res = await axios.get('http://127.0.0.1:5000/api/analytics');
      setAnalytics(res.data);
    }
  };

  return (
    <div className="dashboard-container">
      {/* SIDEBAR */}
      <aside className="sidebar">
        <div className="logo">
          <div className="logo-icon"><ShieldAlert size={20}/></div>
          <span>SpamGuard AI</span>
        </div>
        <div className="nav-links">
          <div className={`nav-item ${activeTab === 'analyzer' ? 'active' : ''}`} onClick={() => switchTab('analyzer')}>
            <Mail size={18}/> Analyzer
          </div>
          <div className={`nav-item ${activeTab === 'history' ? 'active' : ''}`} onClick={() => switchTab('history')}>
            <History size={18}/> History
          </div>
          <div className={`nav-item ${activeTab === 'analytics' ? 'active' : ''}`} onClick={() => switchTab('analytics')}>
            <BarChart3 size={18}/> Analytics
          </div>
        </div>
      </aside>

      {/* MAIN CONTENT AREA */}
      <main className="main-content">
        
        {/* --- 1. ANALYZER TAB --- */}
        {activeTab === "analyzer" && (
          <div className="fade-in">
            <header>
              <h1>Email Intelligence</h1>
              <p>Scan incoming messages for spam patterns and malicious signatures.</p>
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
                  {loading ? <Zap size={18} className="spinning" /> : <Send size={18} />}
                  {loading ? "Analyzing..." : "Run ML Scan"}
                </button>
              </div>
            </section>

            {/* GUARD: Results only show if result is NOT null */}
            {result && (
              <div className="results-grid fade-in">
                <div className="result-item">
                  <div className="status-label">Final Verdict</div>
                  <div className={`status-value ${result.label.includes('Spam') ? 'spam' : 'ham'}`}>
                    {result.label.includes('Spam') ? 'SPAM DETECTED' : 'SECURE / HAM'}
                  </div>
                </div>
                <div className="result-item">
                  <div className="status-label">ML Confidence</div>
                  <div className="status-value">{(result.score * 100).toFixed(1)}%</div>
                </div>
              </div>
            )}
          </div>
        )}

        {/* --- 2. HISTORY TAB --- */}
        {activeTab === "history" && (
          <div className="fade-in">
            <header>
              <h1>Scan Audit Log</h1>
              <p>Review previous analysis results stored in the local database.</p>
            </header>
            <table className="history-table">
              <thead>
                <tr>
                  <th>Timestamp</th>
                  <th>Snippet</th>
                  <th>Result</th>
                  <th>Confidence</th>
                </tr>
              </thead>
              <tbody>
                {history.length > 0 ? history.map((item) => (
                  <tr key={item.id}>
                    <td>{new Date(item.timestamp).toLocaleString()}</td>
                    <td className="text-truncate">{item.text}</td>
                    <td><span className={`badge ${item.label.toLowerCase()}`}>{item.label}</span></td>
                    <td>{(item.score * 100).toFixed(1)}%</td>
                  </tr>
                )) : <tr><td colSpan="4" style={{textAlign: 'center', padding: '40px'}}>No history found.</td></tr>}
              </tbody>
            </table>
          </div>
        )}

        {/* --- 3. ANALYTICS TAB --- */}
        {activeTab === "analytics" && (
          <div className="fade-in">
            <header>
              <h1>ML Analytics</h1>
              <p>Data visualization of detection trends and distribution.</p>
            </header>
            <div className="analytics-grid">
              <div className="glass-card chart-box">
                <h3>Detection Distribution</h3>
                <ResponsiveContainer width="100%" height={300}>
                  <PieChart>
                    <Pie data={analytics} innerRadius={60} outerRadius={80} paddingAngle={5} dataKey="value">
                      {analytics.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.name.includes('Spam') ? '#ef4444' : '#10b981'} />
                      ))}
                    </Pie>
                    <Tooltip contentStyle={{backgroundColor: '#0d1117', border: '1px solid #30363d'}} />
                  </PieChart>
                </ResponsiveContainer>
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
};

export default App;