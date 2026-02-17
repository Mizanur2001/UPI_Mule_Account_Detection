const BASE = '';

export async function fetchDashboardData() {
  const res = await fetch(`${BASE}/api/dashboard`);
  if (!res.ok) throw new Error(`Dashboard API error: ${res.status}`);
  return res.json();
}

export async function fetchNetworkData(maxNodes = 80, riskFilter = 'all') {
  const res = await fetch(`${BASE}/api/network?max_nodes=${maxNodes}&risk_filter=${riskFilter}`);
  if (!res.ok) throw new Error(`Network API error: ${res.status}`);
  return res.json();
}

export async function fetchTimelineData() {
  const res = await fetch(`${BASE}/api/timeline`);
  if (!res.ok) throw new Error(`Timeline API error: ${res.status}`);
  return res.json();
}

export async function fetchReport() {
  const res = await fetch(`${BASE}/api/report`);
  if (!res.ok) throw new Error(`Report API error: ${res.status}`);
  return res.json();
}

export async function scoreAccount(accountId) {
  const res = await fetch(`${BASE}/score/${encodeURIComponent(accountId)}`);
  if (!res.ok) throw new Error(`Score API error: ${res.status}`);
  return res.json();
}

export async function simulateTransaction(sender, receiver, amount) {
  const res = await fetch(`${BASE}/simulate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ sender, receiver, amount }),
  });
  if (!res.ok) throw new Error(`Simulate API error: ${res.status}`);
  return res.json();
}

export function downloadFile(content, filename, mimeType) {
  const blob = new Blob([content], { type: mimeType });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}
