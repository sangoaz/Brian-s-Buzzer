export default function TeamAssignment({
  players = [],
  teams = [],
  onAssignTeam,
}) {
  if (teams.length === 0) return null

  return (
    <section className="rounded-3xl bg-zinc-900 border border-zinc-800 p-6 mb-6 text-left">
      <h2 className="text-2xl font-black mb-1">Équipes</h2>
      <p className="text-zinc-400 text-sm mb-4">
        Assigne chaque joueur à une équipe avant de lancer la partie.
      </p>

      {players.length === 0 ? (
        <p className="text-zinc-500">Aucun joueur pour le moment.</p>
      ) : (
        <ul className="space-y-3">
          {players.map((player) => (
            <li
              key={player.id}
              className="bg-zinc-800 rounded-xl px-4 py-3"
            >
              <div className="flex items-center justify-between mb-2">
                <span className="font-bold">{player.name}</span>
              </div>

              <div className="flex flex-wrap gap-2">
                {teams.map((team) => (
                  <button
                    key={team.id}
                    onClick={() => onAssignTeam(player.id, team.id)}
                    className={`px-3 py-1 rounded-lg text-sm font-bold transition ${
                      player.team_id === team.id
                        ? "bg-red-600 text-white"
                        : "bg-zinc-700 hover:bg-zinc-600 text-zinc-300"
                    }`}
                  >
                    {team.name}
                  </button>
                ))}

                {player.team_id && (
                  <button
                    onClick={() => onAssignTeam(player.id, null)}
                    className="px-3 py-1 rounded-lg text-sm font-bold bg-zinc-800 hover:bg-zinc-700 text-zinc-500 transition"
                  >
                    Retirer
                  </button>
                )}
              </div>
            </li>
          ))}
        </ul>
      )}
    </section>
  )
}
