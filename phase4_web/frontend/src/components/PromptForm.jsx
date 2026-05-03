// components/PromptForm.jsx
import { useState } from 'react'

export default function PromptForm({ onSubmit, disabled }) {
  const [prompt, setPrompt] = useState('')

  const handleSubmit = (e) => {
    e.preventDefault()
    if (prompt.trim()) onSubmit(prompt.trim())
  }

  return (
    <form onSubmit={handleSubmit} className="flex flex-col gap-4">
      <label className="text-sm font-semibold text-indigo-300 uppercase tracking-widest">
        Your Story Prompt
      </label>
      <textarea
        id="prompt-input"
        rows={3}
        value={prompt}
        onChange={(e) => setPrompt(e.target.value)}
        disabled={disabled}
        placeholder="e.g. A young astronaut discovers a hidden ocean on Mars..."
        className="w-full rounded-xl bg-gray-800 border border-gray-700 p-4 text-gray-100
                   placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-indigo-500
                   resize-none transition"
      />
      <button
        id="generate-btn"
        type="submit"
        disabled={disabled || !prompt.trim()}
        className="self-end px-8 py-3 rounded-xl bg-indigo-600 hover:bg-indigo-500
                   disabled:opacity-40 disabled:cursor-not-allowed text-white font-semibold
                   transition-all duration-200 shadow-lg shadow-indigo-900/40"
      >
        {disabled ? '⏳ Generating…' : '🎬 Generate Video'}
      </button>
    </form>
  )
}
