// components/VideoPlayer.jsx
export default function VideoPlayer({ videoUrl }) {
  if (!videoUrl) return null
  const src = videoUrl.startsWith('/api') ? videoUrl : `/api/download/final_output.mp4`

  return (
    <div className="flex flex-col gap-3">
      <h2 className="text-sm font-semibold text-indigo-300 uppercase tracking-widest">
        Generated Video
      </h2>
      <video
        id="output-video"
        src={src}
        controls
        autoPlay
        className="w-full rounded-xl border border-gray-700 shadow-2xl shadow-indigo-900/20"
      />
      <a
        href={src}
        download="agenticai_output.mp4"
        className="self-start px-5 py-2 rounded-lg bg-gray-800 hover:bg-gray-700
                   text-sm text-gray-200 transition border border-gray-700"
      >
        ⬇ Download MP4
      </a>
    </div>
  )
}
