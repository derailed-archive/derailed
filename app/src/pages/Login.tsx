import { FormEvent, useState } from "react"
import JSON from "json-bigint"
import { useNavigate, Navigate } from "react-router-dom"
import { User } from "../types"

interface Response {
    token: string,
    // not important to us
    user: User,
}

export default function Login() {
    if (typeof window !== 'undefined') {
        if (localStorage.getItem("token") !== null) {
            return <Navigate to="/users/@me" />
        }
    }

    const nav = useNavigate()
    const [username, setUsername] = useState<string>()
    const [password, setPassword] = useState<string>()

    const [displayError, setDisplay] = useState<boolean>()
    const [error, setError] = useState<string>()

    const onSubmit = (event: FormEvent) => {
        event.preventDefault()

        fetch(
            import.meta.env.VITE_API_URL! + "/login",
            {
                body: JSON.stringify({
                    username,
                    password,
                }),
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                }
            }
        ).then(async (resp) => {
            const body = JSON.parse(await resp.text()) as Response

            localStorage.setItem("token", body.token)
            nav("/users/@me")
        }).catch((reason: Error) => {
            console.error(reason)
            setError(reason.toString())
            setDisplay(true)
        })
    }

    return (
      <main className="flex min-h-screen bg-no-repeat antialiased bg-cover bg-trains-away font-primary">
        {displayError && (
            <div className="text-center">
                {error}
            </div>
        )}
        <form className="flex flex-col p-10 rounded items-center m-auto bg-quite-blue justify-center text-center gap-6 text-blackbird" onSubmit={onSubmit}>
            <h1 className="text-unrailed text-2xl max-w-xl">
                Welcome back!
            </h1>
            <section className="flex flex-col gap-0.5 m-auto">
                <label className="text-left">Username</label>
                <input className="bg-quite-more-blue rounded p-1" type="text" id="username" minLength={1} maxLength={32} onChange={(event) => {setUsername(event.target.value)}} required />
            </section>
            <section className="flex flex-col gap-0.5 m-auto">
                <label className="text-left">Password</label>
                <input className="bg-quite-more-blue rounded p-1" type="password" id="password" minLength={1} maxLength={32} onChange={(event) => {setPassword(event.target.value)}} required />
            </section>
            <button type="submit" className="bg-quite-more-blue text-xl m-auto py-2 px-8 rounded-2xl">
                Login
            </button>
            <div>
                Don't have an account? <a className="text-unrailed font-medium" href="/register">Register</a> instead.
            </div>
        </form>
      </main>
    )
  }
