import Link from "next/link"

export default function HomePage() {
  return (
    <main className="min-h-screen flex items-center justify-center bg-zinc-950 text-white px-6">
      <div className="w-full max-w-md text-center">
        <h1 className="text-5xl font-black mb-4">Brian&apos;s Buzzer</h1>

        <p className="text-zinc-400 mb-10">
          Le buzzer simple pour quiz, blind tests et soirées entre amis.
        </p>

        <div className="flex flex-col gap-4">
          <Link
            href="/create"
            className="bg-red-600 hover:bg-red-700 transition rounded-2xl py-4 font-bold text-lg"
          >
            Créer une partie
          </Link>

          <Link
            href="/join"
            className="bg-zinc-800 hover:bg-zinc-700 transition rounded-2xl py-4 font-bold text-lg"
          >
            Rejoindre une partie
          </Link>
        </div>
      </div>
    </main>
  )
}