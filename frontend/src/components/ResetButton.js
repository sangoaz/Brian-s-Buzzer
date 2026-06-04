export default function ResetButton({
  onReset,
  disabled = false,
}) {
  return (
    <button
      onClick={onReset}
      disabled={disabled}
      className="
        bg-red-600
        hover:bg-red-700
        disabled:bg-zinc-800
        disabled:text-zinc-500
        disabled:cursor-not-allowed
        transition
        rounded-2xl
        px-10
        py-4
        font-black
        text-xl
        mb-10
      "
    >
      Manche suivante
    </button>
  )
}