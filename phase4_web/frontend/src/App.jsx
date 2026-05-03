// App.jsx — Main application layout
import { usePipeline } from './hooks/usePipeline'
import PromptForm     from './components/PromptForm'
import PipelineStatus from './components/PipelineStatus'
import VideoPlayer    from './components/VideoPlayer'
import EditPanel      from './components/EditPanel'
import VersionHistory from './components/VersionHistory'

export default function App() {
  const { jobId, status, progress, message, videoUrl, events, run, edit } = usePipeline()
  const isRunning = status === 'running'
  const isDone    = status === 'done'

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-950 via-gray-900 to-indigo-950">
      {/* Header */}
      <header className="border-b border-gray-800 px-8 py-5 flex items-center gap-4">
        <span className="text-2xl">🎬</span>
        <div>
          <h1 className="text-xl font-bold text-white">AgenticAI Video Generator</h1>
          <p className="text-xs text-gray-500">AI-Powered Animated Video from Text Prompt</p>
        </div>
        {jobId && (
          <span className="ml-auto text-xs font-mono text-gray-500">
            Job: <span className="text-indigo-400">{jobId}</span>
          </span>
        )}
      </header>

      <main className="max-w-3xl mx-auto px-6 py-10 flex flex-col gap-10">
        {/* Prompt Input */}
        <section className="bg-gray-900/70 backdrop-blur rounded-2xl border border-gray-800 p-6 shadow-xl">
          <PromptForm onSubmit={run} disabled={isRunning} />
        </section>

        {/* Pipeline Progress */}
        {(isRunning || isDone) && (
          <section className="bg-gray-900/70 backdrop-blur rounded-2xl border border-gray-800 p-6 shadow-xl">
            <PipelineStatus
              events={events}
              progress={progress}
              message={message}
              status={status}
            />
          </section>
        )}

        {/* Video Player */}
        {(isDone || videoUrl) && (
          <section className="bg-gray-900/70 backdrop-blur rounded-2xl border border-gray-800 p-6 shadow-xl">
            <VideoPlayer videoUrl={videoUrl} />
          </section>
        )}

        {/* Edit Panel */}
        {isDone && (
          <section className="bg-gray-900/70 backdrop-blur rounded-2xl border border-gray-800 p-6 shadow-xl">
            <EditPanel onEdit={edit} disabled={isRunning} />
          </section>
        )}

        {/* Version History */}
        {isDone && (
          <section className="bg-gray-900/70 backdrop-blur rounded-2xl border border-gray-800 p-6 shadow-xl">
            <VersionHistory />
          </section>
        )}
      </main>
    </div>
  )
}
