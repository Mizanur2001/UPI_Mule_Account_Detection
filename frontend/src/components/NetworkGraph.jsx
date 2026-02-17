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
  const containerRef = useRef(null);
  const networkRef = useRef(null);

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
    })));

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
