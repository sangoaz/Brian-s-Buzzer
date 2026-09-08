import type { Player, Team } from "../types/room"

interface PlayerListProps {
  players?: Player[]
  onKickPlayer?: ((playerId: string) => void) | null
  scores?: Record<string, number>
  teams?: Team[]
}

export default function PlayerList({
  players = [],
  onKickPlayer = null,
  scores,
  teams = [],
}: PlayerListProps) {
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
          {players.map((player) => {
            const team = teams.find((t) => t.id === player.team_id)

            return (
              <li
                key={player.id}
                className="bg-zinc-800 rounded-xl px-4 py-3 flex justify-between items-center"
              >
                <span className="font-bold">
                  {player.name}
                  {team && (
                    <span className="ml-2 text-xs font-normal text-zinc-500">
                      {team.name}
                    </span>
                  )}
                </span>

                <div className="flex items-center gap-3">
                  {scores && (
                    <span className="text-red-400 font-black text-xl">
                      {scores[player.id] ?? 0}
                    </span>
                  )}

                  {onKickPlayer && (
                    <button
                      onClick={() => onKickPlayer(player.id)}
                      className="
                        px-3
                        py-1
                        rounded-lg
                        text-sm
                        font-bold
                        bg-red-600
                        hover:bg-red-700
                        transition
                      "
                    >
                      Déconnecter
                    </button>
                  )}
                </div>
              </li>
            )
          })}
        </ul>
      )}
    </section>
  )
}
