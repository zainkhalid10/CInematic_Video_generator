// components/PipelineStatus.jsx
const PHASES = [
  { id: 1, label: 'Story & Script' },
  { id: 2, label: 'Audio Synthesis' },
  { id: 3, label: 'Video Composition' },
]

export default function PipelineStatus({ events, progress, message, status }) {
  const currentPhase = events.length ? events[events.length - 1]?.phase ?? 0 : 0

  return (
    <div className="flex flex-col gap-4">
      {/* Overall progress bar */}
      <div>
        <div className="flex justify-between text-xs text-gray-400 mb-1">
          <span>{message || 'Waiting to start…'}</span>
          <span>{Math.round(progress * 100)}%</span>
        </div>
        <div className="h-2 bg-gray-800 rounded-full overflow-hidden">
          <div
            className="h-full bg-indigo-500 transition-all duration-500"
            style={{ width: `${progress * 100}%` }}
          />
        </div>
      </div>

      {/* Phase indicators */}
      <div className="flex gap-3">
        {PHASES.map((p) => {
          const done    = currentPhase > p.id || status === 'done'
          const active  = currentPhase === p.id && status === 'running'
          return (
            <div
              key={p.id}
              className={`flex-1 rounded-lg p-3 text-center text-sm font-medium border transition
                ${done   ? 'bg-indigo-900/50 border-indigo-500 text-indigo-300' : ''}
                ${active ? 'bg-indigo-800/40 border-indigo-400 text-white animate-pulse' : ''}
                ${!done && !active ? 'bg-gray-800/50 border-gray-700 text-gray-500' : ''}
              `}
            >
              {done ? '✓ ' : active ? '⚡ ' : `${p.id}. `}{p.label}
            </div>
          )
        })}
      </div>

      {/* Event log */}
      {events.length > 0 && (
        <div className="bg-gray-900 rounded-lg p-3 max-h-32 overflow-y-auto text-xs font-mono text-gray-400 space-y-0.5">
          {events.slice(-10).map((e, i) => (
            <div key={i}>
              <span className="text-indigo-400">[Phase {e.phase}]</span> {e.message}
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
