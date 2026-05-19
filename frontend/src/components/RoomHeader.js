export default function RoomHeader({ roomCode, subtitle }) {
  return (
    <>
      <p className="text-zinc-400 mb-2">{subtitle}</p>

      <h1 className="text-5xl md:text-7xl font-black mb-8">
        {roomCode}
      </h1>
    </>
  )
}