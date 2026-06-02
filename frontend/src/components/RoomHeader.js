import { useState } from "react"

export default function RoomHeader({
  roomCode,
  playerCount = 0,
}) {
  const [copied, setCopied] = useState(false)

  async function handleCopy() {
    await navigator.clipboard.writeText(roomCode)
    setCopied(true)
    setTimeout(() => {
      setCopied(false)
    }, 2000)
  }

  return (
    <div className="flex justify-between items-center p-4">
      <div>
        <h1
          onClick={handleCopy}
          className="text-xl font-bold cursor-pointer hover:text-red-400 transition"
        >
          Salon : {copied ? "Copié !" : roomCode}
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