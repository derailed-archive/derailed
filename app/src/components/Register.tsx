import { useState, FormEvent } from "react"
import { Navigate, useNavigate } from "react-router-dom"
import superjson from "superjson"
import { User } from "../types"

interface RegisterResponse {
    user: User,
    token: string
}

export default () => {
    if (localStorage.getItem("token") !== null) {
        return <Navigate to="/channels/@me"></Navigate>
    }

    const navigate = useNavigate()
    const [username, setUsername] = useState<string | null>(null)
    const [password, setPassword] = useState<string | null>(null)

    const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
        event.preventDefault()

        const API_URL: string = import.meta.env.VITE_API_URL

        try {
            let resp = await fetch(
                API_URL.concat("/register"),
                {
                    method: "POST",
                    body: JSON.stringify({
                        'username': username!,
                        'password': password!
                    }),
                    mode: 'cors',
                    headers: {
                        "Content-Type": "application/json"
                    },
                },
            )

            if (resp.status == 201) {
                let json = superjson.parse<RegisterResponse>(await resp.text())
                localStorage.setItem("token", json.token)
                navigate("/")
            } else {
                console.error(await resp.text())
                let err_json = superjson.parse<object>(await resp.text())

                if ('code' in err_json && err_json.code === 2002) {
                    // TODO!: show this to the user.
                    console.error("Username taken")
                }
            }
        } catch {
            navigate("/register")
        }
    }

    return (
        <main className="bg-no-repeat antialiased font-primary m-auto text-white bg-cover min-h-screen flex flex-col justify-center items-center" style={{backgroundImage: "url('/assets/trains-away.jpg')"}}>
            <div className="bg-quite-blue rounded p-7 rounded-3">
                <h1 className="font-semibold select-none text-2xl pb-2 max-w-sm text-center text-blackbird">
                    Welcome to <div className="text-unrailed">Derailed!</div>
                </h1>

                <form className="flex flex-col gap-5" onSubmit={handleSubmit}>
                    <section className="flex flex-col gap-5">
                        <div className="flex flex-col gap-1">
                            <label className="select-none text-blackbird pl-1">Username</label>
                            <input className="rounded bg-quite-more-blue border-0 p-2 text-white" type="text" id="username" minLength={1} maxLength={32} onChange={(event) => {setUsername(event.target.value)}} required />
                        </div>
                        <div className="flex flex-col gap-1">
                            <label className="select-none text-blackbird pl-1">Password</label>
                            <input className="rounded bg-quite-more-blue border-0 p-2 text-white" type="password" id="password" minLength={1} maxLength={70} onChange={(event) => {setPassword(event.target.value)}} required />
                        </div>
                    </section>
                    <button type="submit" className="text-white outline-0 text-lg hover:bg-unrailed font-primary font-400 rounded-2 py-1 px-20 bg-quite-more-blue">
                            Register
                    </button>
                    <h5 className="text-blackbird">
                        Already have an account? <a href="/login" className="no-underline text-unrailed">
                            Login
                        </a> instead.
                    </h5>
                </form>
            </div>
        </main>
    )
}