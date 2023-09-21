import { useState, FormEvent } from "react"
import { Navigate, useNavigate } from "react-router-dom"
import { toJSON } from "../util"
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
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: toJSON({
                        'username': username!,
                        'password': password!
                    })
                }
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
            <div className="bg-quite-blue rounded p-3 rounded-3">
                <h1 className="font-semibold text-2xl pb-10 max-w-sm text-center">
                    Now Boarding the Derailed Train.
                </h1>

            </div>
        </main>
    )
}