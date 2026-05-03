// components/EditPanel.jsx
import { useState } from 'react'

export default function EditPanel({ onEdit, disabled }) {
  const [command, setCommand] = useState('')
  const [result, setResult]   = useState(null)
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!command.trim() || disabled) return
    setLoading(true)
    try {
      const res = await onEdit(command.trim())
      setResult(res)
      setCommand('')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="flex flex-col gap-3">
      <h2 className="text-sm font-semibold text-purple-300 uppercase tracking-widest">
        Edit Video
      </h2>
      <form onSubmit={handleSubmit} className="flex gap-2">
        <input
          id="edit-command-input"
          type="text"
          value={command}
          onChange={(e) => setCommand(e.target.value)}
          disabled={disabled || loading}
          placeholder='e.g. "Apply sepia filter to scene 1"'
          className="flex-1 rounded-lg bg-gray-800 border border-gray-700 px-4 py-2 text-sm
                     text-gray-100 placeholder-gray-500 focus:outline-none focus:ring-2
                     focus:ring-purple-500 transition"
        />
        <button
          id="edit-submit-btn"
          type="submit"
          disabled={disabled || loading || !command.trim()}
          className="px-5 py-2 rounded-lg bg-purple-700 hover:bg-purple-600 disabled:opacity-40
                     text-sm text-white font-semibold transition"
        >
          {loading ? '⏳' : 'Apply'}
        </button>
      </form>

      {result && (
        <div className="bg-gray-900 rounded-lg p-3 text-xs font-mono space-y-1">
          <div className="text-purple-400 font-semibold">
            ✓ {result.intent?.action} on {result.intent?.target} — v{result.version}
          </div>
          {result.changes_made?.map((c, i) => (
            <div key={i} className="text-gray-400">· {c}</div>
          ))}
        </div>
      )}
    </div>
  )
}
