// components/VersionHistory.jsx
import { useEffect, useState } from 'react'
import { getHistory, revertVersion } from '../api/client'

export default function VersionHistory() {
  const [history, setHistory]   = useState([])
  const [reverting, setReverting] = useState(null)

  const load = async () => {
    try {
      const data = await getHistory()
      setHistory(data)
    } catch { /* backend not ready yet */ }
  }

  useEffect(() => { load() }, [])

  const handleRevert = async (version) => {
    setReverting(version)
    await revertVersion(version)
    setReverting(null)
    await load()
  }

  if (!history.length) return null

  return (
    <div className="flex flex-col gap-3">
      <h2 className="text-sm font-semibold text-amber-300 uppercase tracking-widest">
        Version History
      </h2>
      <div className="space-y-2">
        {history.map((v) => (
          <div
            key={v.version}
            className="flex items-center justify-between bg-gray-800/60 rounded-lg px-4 py-2
                       border border-gray-700"
          >
            <div>
              <span className="text-amber-400 font-mono text-xs">v{v.version}</span>
              <span className="ml-3 text-gray-300 text-sm">{v.summary || '(no summary)'}</span>
              <span className="ml-3 text-gray-500 text-xs">{v.created_at?.slice(0, 19)}</span>
            </div>
            <button
              id={`revert-v${v.version}`}
              onClick={() => handleRevert(v.version)}
              disabled={reverting === v.version}
              className="text-xs px-3 py-1 rounded bg-amber-800/40 hover:bg-amber-700/50
                         text-amber-300 border border-amber-700/50 transition disabled:opacity-40"
            >
              {reverting === v.version ? '↩…' : '↩ Revert'}
            </button>
          </div>
        ))}
      </div>
    </div>
  )
}
