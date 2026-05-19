export default function BuzzerButton({ disabled, onBuzz }) {
  return (
    <button
      onClick={onBuzz}
      disabled={disabled}
      className="w-64 h-64 rounded-full bg-red-600 hover:bg-red-700 disabled:bg-zinc-700 disabled:text-zinc-400 transition text-4xl font-black shadow-2xl"
    >
      BUZZ
    </button>
  )
}