export default function PlayerList({ players }) {
  return (
    <section className="rounded-3xl bg-zinc-900 border border-zinc-800 p-6 text-left">
      <h2 className="text-2xl font-black mb-4">
        Joueurs connectés
      </h2>

      {players.length === 0 ? (
        <p className="text-zinc-500">
          Aucun joueur pour le moment.
        </p>
      ) : (
        <ul className="space-y-3">
          {players.map((player) => (
            <li
              key={player.id}
              className="bg-zinc-800 rounded-xl px-4 py-3 font-bold"
            >
              {player.name}
            </li>
          ))}
        </ul>
      )}
    </section>
  )
}