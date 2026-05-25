export default function RoomHeader({
  roomCode,
  playerCount = 0,
}) {
  return (
    <div className="flex justify-between items-center p-4">
      <div>
        <h1 className="text-xl font-bold">
          Salon : {roomCode}
        </h1>
      </div>

      <div
        className="px-3 py-1 rounded-full text-sm text-black"
        style={{
          background: "#f3f4f6",
        }}
      >
        👥 {playerCount} joueur{playerCount > 1 ? "s" : ""}
      </div>
    </div>
  )
}