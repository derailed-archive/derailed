"use client"

import { FormEvent, useState } from "react"
import JSON from "json-bigint"
import { RedirectType, redirect } from "next/navigation"

interface Response {
    token: string,
    // not important to us
    user: object,
}

export default function Register() {
    if (typeof window !== 'undefined') {
        if (localStorage.getItem("token") !== null) {
            redirect("/users/@me", RedirectType.push)
        }
    }

    const [username, setUsername] = useState<string>()
    const [password, setPassword] = useState<string>()

    const [displayError, setDisplay] = useState<boolean>(false)
    const [error, setError] = useState<any>()

    const onSubmit = (event: FormEvent) => {
        event.preventDefault()

        fetch(
            process.env.NEXT_PUBLIC_API_URL! + "/register",
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
            redirect("/users/@me")
        }).catch((reason) => {
            console.error(reason)
            setError(reason)
            setDisplay(true)
        })
    }

    return (
      <main className="flex min-h-screen bg-no-repeat antialiased bg-cover bg-trains-away">
        {displayError && (
            <div className="text-center">
                {error}
            </div>
        )}
        <form className="flex flex-col p-10 rounded items-center m-auto bg-quite-blue justify-center text-center gap-6 text-blackbird" onSubmit={onSubmit}>
            <h1 className="text-blackbird text-2xl max-w-xl">
                Welcome to <h1 className="text-unrailed font-semibold">Derailed.</h1>
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
                Register
            </button>
            <div>
                Already have an account? <a className="text-unrailed font-medium" href="/login">Login</a> instead.
            </div>
        </form>
      </main>
    )
  }
