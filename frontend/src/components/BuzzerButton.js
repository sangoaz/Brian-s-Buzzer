export default function BuzzerButton({ disabled, onBuzz, iAmTheBuzzer = false, isBlocked = false }) {
  const baseClass = "w-64 h-64 rounded-full transition text-4xl font-black shadow-2xl"

  const colorClass = iAmTheBuzzer
    ? "bg-green-500 text-white animate-bounce"
    : isBlocked
    ? "bg-orange-600 text-white cursor-not-allowed"
    : disabled
    ? "bg-zinc-700 text-zinc-400 cursor-not-allowed"
    : "bg-red-600 hover:bg-red-700 text-white"

  const label = iAmTheBuzzer
    ? "BUZZÉ !"
    : isBlocked
    ? "BLOQUÉ"
    : "BUZZ"

  return (
    <button
      onClick={onBuzz}
      disabled={disabled}
      className={`${baseClass} ${colorClass}`}
    >
      {label}
    </button>
  )
}