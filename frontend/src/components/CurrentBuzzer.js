export default function CurrentBuzzer({ currentBuzzer, large = false }) {
  return (
    <section className="mb-10 rounded-3xl bg-zinc-900 border border-zinc-800 p-8">
      <p className="text-zinc-400 mb-4">Premier buzzer</p>

      {currentBuzzer ? (
        <p className={`${large ? "text-6xl" : "text-3xl"} font-black text-red-500`}>
          {currentBuzzer.name}
        </p>
      ) : (
        <p className={`${large ? "text-3xl" : "text-base"} font-bold text-zinc-500`}>
          En attente...
        </p>
      )}
    </section>
  )
}