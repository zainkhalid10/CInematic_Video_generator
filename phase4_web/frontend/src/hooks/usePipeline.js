// hooks/usePipeline.js
import { useState, useCallback } from 'react'
import { startPipeline, submitEdit, revertVersion } from '../api/client'
import { useWebSocket } from './useWebSocket'

export function usePipeline() {
  const [jobId, setJobId]       = useState(null)
  const [status, setStatus]     = useState('idle')   // idle | running | done | failed
  const [progress, setProgress] = useState(0)
  const [message, setMessage]   = useState('')
  const [videoUrl, setVideoUrl] = useState(null)
  const [events, setEvents]     = useState([])

  const handleWsMessage = useCallback((event) => {
    setEvents((prev) => [...prev, event])
    setProgress(event.progress ?? 0)
    setMessage(event.message ?? '')
    if (event.status === 'done') setStatus('done')
    if (event.status === 'error') setStatus('failed')
    if (event.video_url) setVideoUrl(event.video_url)
  }, [])

  useWebSocket(jobId, handleWsMessage)

  const run = useCallback(async (prompt) => {
    setStatus('running')
    setProgress(0)
    setEvents([])
    setVideoUrl(null)
    const data = await startPipeline(prompt)
    setJobId(data.job_id)
  }, [])

  const edit = useCallback(async (command) => {
    if (!jobId) return
    return submitEdit(jobId, command)
  }, [jobId])

  const revert = useCallback(async (version) => {
    return revertVersion(version)
  }, [])

  return { jobId, status, progress, message, videoUrl, events, run, edit, revert }
}
