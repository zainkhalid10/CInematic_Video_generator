// src/api/client.js — Axios-style fetch wrapper for all API calls

const BASE = '/api'

export async function startPipeline(prompt) {
  const res = await fetch(`${BASE}/run`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ prompt }),
  })
  return res.json()
}

export async function getStatus(jobId) {
  const res = await fetch(`${BASE}/status/${jobId}`)
  return res.json()
}

export async function submitEdit(jobId, command) {
  const res = await fetch(`${BASE}/edit`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ job_id: jobId, command }),
  })
  return res.json()
}

export async function getHistory() {
  const res = await fetch(`${BASE}/history`)
  return res.json()
}

export async function revertVersion(version) {
  const res = await fetch(`${BASE}/revert`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ version }),
  })
  return res.json()
}
