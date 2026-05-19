export default function ResetButton({ onReset }) {
  return (
    <button
      onClick={onReset}
      className="bg-red-600 hover:bg-red-700 transition rounded-2xl px-10 py-4 font-black text-xl mb-10"
    >
      RESET
    </button>
  )
}