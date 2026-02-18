import React, { useState, useEffect, useRef } from 'react';
import { Network } from 'vis-network/standalone';
import { DataSet } from 'vis-data/standalone';
import Icon from './Icon';
import { fetchNetworkData } from '../api';

export default function NetworkGraph() {
  const [showGraph, setShowGraph] = useState(true);
  const [maxNodes, setMaxNodes] = useState(80);
  const [riskFilter, setRiskFilter] = useState('all');
  const [graphData, setGraphData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [selectedNode, setSelectedNode] = useState(null);
  const containerRef = useRef(null);
  const networkRef = useRef(null);
  const nodesRef = useRef(null);

  useEffect(() => {
    if (!showGraph) return;
    setLoading(true);
    fetchNetworkData(maxNodes, riskFilter)
      .then(d => { setGraphData(d); setLoading(false); })
      .catch(() => setLoading(false));
  }, [showGraph, maxNodes, riskFilter]);

  useEffect(() => {
    if (!containerRef.current || !graphData) return;

    if (networkRef.current) {
      networkRef.current.destroy();
      networkRef.current = null;
    }

    const nodes = new DataSet(graphData.nodes.map(n => ({
      id: n.id,
      label: n.label,
      color: n.color,
      size: n.size,
      title: n.title,
      font: { color: '#1f2937', size: 10 },
      _originalColor: n.color,
      _originalSize: n.size,
    })));
    nodesRef.current = nodes;

    const edges = new DataSet(graphData.edges.map((e, i) => ({
      id: `e-${i}`,
      from: e.from,
      to: e.to,
      value: e.value,
      title: e.title,
      color: { color: '#9ca3af', opacity: 0.6 },
    })));

    const options = {
      nodes: {
        shape: 'dot',
        borderWidth: 0,
      },
      edges: {
        arrows: { to: { enabled: true, scaleFactor: 0.5 } },
        smooth: { type: 'continuous' },
      },
      physics: {
        barnesHut: {
          gravitationalConstant: -3000,
          centralGravity: 0.3,
          springLength: 200,
        },
      },
      interaction: {
        hover: true,
        tooltipDelay: 100,
      },
    };

    networkRef.current = new Network(containerRef.current, { nodes, edges }, options);

    return () => {
      if (networkRef.current) {
        networkRef.current.destroy();
        networkRef.current = null;
      }
    };
  }, [graphData]);

  // Search handler
  const handleSearch = (query) => {
    setSearchQuery(query);
    setSelectedNode(null);

    if (!nodesRef.current || !query.trim()) {
      setSearchResults([]);
      // Reset all nodes to original appearance
      if (nodesRef.current) {
        const updates = [];
        nodesRef.current.forEach(n => {
          updates.push({ id: n.id, color: n._originalColor, size: n._originalSize, opacity: 1 });
        });
        nodesRef.current.update(updates);
      }
      return;
    }

    const q = query.toLowerCase();
    const matches = [];
    const updates = [];
    nodesRef.current.forEach(n => {
      const isMatch = n.label.toLowerCase().includes(q);
      if (isMatch) matches.push({ id: n.id, label: n.label, color: n._originalColor });
      updates.push({
        id: n.id,
        color: isMatch ? n._originalColor : '#3a3a4a',
        size: isMatch ? Math.max(n._originalSize, 18) : Math.max(n._originalSize * 0.6, 4),
        opacity: isMatch ? 1 : 0.3,
      });
    });
    nodesRef.current.update(updates);
    setSearchResults(matches);
  };

  const focusNode = (nodeId) => {
    setSelectedNode(nodeId);
    if (networkRef.current) {
      networkRef.current.focus(nodeId, { scale: 1.5, animation: { duration: 600, easingFunction: 'easeInOutQuad' } });
      networkRef.current.selectNodes([nodeId]);
    }
  };

  const FILTER_OPTIONS = [
    { value: 'all',           label: 'All Accounts' },
    { value: 'critical_high', label: 'Critical + High Only' },
    { value: 'high_medium',   label: 'High + Medium' },
    { value: 'critical',      label: 'Critical Only' },
  ];

  return (
    <div>
      <h2><Icon name="hub" size={24} style={{ marginRight: 8 }} />Transaction Network Visualization</h2>

      <div className="grid-row cols-3">
        <div className="checkbox-row">
          <input type="checkbox" checked={showGraph}
                 onChange={e => setShowGraph(e.target.checked)} />
          <span>Render Graph</span>
        </div>
        <div className="form-group">
          <label>Max Nodes: {maxNodes}</label>
          <input type="range" min={20} max={500} value={maxNodes}
                 onChange={e => setMaxNodes(Number(e.target.value))} />
        </div>
        <div className="form-group">
          <label>Show</label>
          <select value={riskFilter} onChange={e => setRiskFilter(e.target.value)}>
            {FILTER_OPTIONS.map(o => (
              <option key={o.value} value={o.value}>{o.label}</option>
            ))}
          </select>
        </div>
      </div>

      {/* Search bar */}
      <div className="network-search-bar">
        <div className="alert-search">
          <Icon name="search" size={18} />
          <input
            type="text"
            placeholder="Search nodes by account name..."
            value={searchQuery}
            onChange={e => handleSearch(e.target.value)}
          />
          {searchQuery && (
            <button className="alert-search-clear" onClick={() => handleSearch('')}>
              <Icon name="close" size={16} />
            </button>
          )}
        </div>
        {searchResults.length > 0 && (
          <div className="network-search-results">
            <span className="network-search-count">{searchResults.length} found</span>
            <div className="network-search-chips">
              {searchResults.slice(0, 12).map(r => (
                <button
                  key={r.id}
                  className={`network-search-chip ${selectedNode === r.id ? 'active' : ''}`}
                  onClick={() => focusNode(r.id)}
                >
                  <span className="network-chip-dot" style={{ background: r.color }} />
                  {r.label}
                </button>
              ))}
              {searchResults.length > 12 && (
                <span className="network-search-more">+{searchResults.length - 12} more</span>
              )}
            </div>
          </div>
        )}
        {searchQuery && searchResults.length === 0 && (
          <p style={{ margin: '0.4rem 0 0', fontSize: '0.82rem', color: 'var(--text-muted)' }}>
            No nodes match "{searchQuery}"
          </p>
        )}
      </div>

      {showGraph && (
        <div className="network-container">
          {loading ? (
            <div style={{ height: 700, display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#888' }}>
              Building network visualization...
            </div>
          ) : (
            <div ref={containerRef} style={{ height: 700, width: '100%', background: '#0e0e1a' }} />
          )}
        </div>
      )}

      <p style={{ marginTop: '1rem', color: '#aaa', fontSize: '0.9rem' }}>
        <strong>Legend:</strong>{' '}
        <Icon name="circle" size={12} color="#ef4444" /> Critical (85+) · <Icon name="circle" size={12} color="#f97316" /> High (70-84) · <Icon name="circle" size={12} color="#eab308" /> Medium (40-69) · <Icon name="circle" size={12} color="#22c55e" /> Low (&lt;40)
        <br />
        <em>Node size = risk severity. Hover for details. Drag to rearrange.</em>
      </p>
    </div>
  );
}
