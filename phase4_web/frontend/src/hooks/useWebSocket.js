// hooks/useWebSocket.js
import { useEffect, useRef, useCallback } from 'react'

export function useWebSocket(jobId, onMessage) {
  const wsRef = useRef(null)

  useEffect(() => {
    if (!jobId) return
    const ws = new WebSocket(`ws://localhost:8000/ws/progress/${jobId}`)
    wsRef.current = ws

    ws.onmessage = (e) => {
      try {
        const data = JSON.parse(e.data)
        onMessage(data)
      } catch { /* ignore */ }
    }

    ws.onerror = (e) => console.error('[WS] error', e)
    return () => ws.close()
  }, [jobId])

  const send = useCallback((msg) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(msg))
    }
  }, [])

  return { send }
}
