import { useState, FormEvent } from "react"
import { Navigate, useNavigate } from "react-router-dom"
import JSON from "json-bigint"
import { User } from "../types"

interface LoginResponse {
    token: string,
    user: User,
}

export default () => {
    if (localStorage.getItem("token") !== null) {
        return <Navigate to="/channels/@me"></Navigate>
    }

    const navigate = useNavigate()
    const [username, setUsername] = useState<string | null>(null)
    const [password, setPassword] = useState<string | null>(null)
    const [displayAlert, setDisplay] = useState<boolean>(false)
    const [alert, setAlert] = useState<string>("")

    const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
        event.preventDefault()

        const API_URL: string = import.meta.env.VITE_API_URL

        try {
            let resp = await fetch(
                API_URL.concat("/login"),
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

            if (resp.status == 200) {
                const text = await resp.text()
                let json = JSON.parse(text) as LoginResponse
                console.log(text)
                console.log(json)
                console.log(json.token)
                localStorage.setItem("token", json['token'])
                navigate("/")
            } else {
                console.error(await resp.text())
                let err_json = JSON.parse(await resp.text()) as object

                if ('code' in err_json && err_json.code === 2004) {
                    setAlert("Invalid Username!")
                    setDisplay(true)
                } else if ('code' in err_json && err_json.code === 2003) {
                    setAlert("Invalid Username!")
                    setDisplay(true)
                }
            }
        // @ts-ignore
        } catch(err: Error) {
            setAlert(err)
            setDisplay(true)
        }
    }

    return (
        <main className="bg-no-repeat antialiased font-primary m-auto text-white bg-cover min-h-screen flex flex-col justify-center items-center" style={{backgroundImage: "url('/assets/trains-away.jpg')"}}>
            {displayAlert && (
                <div className="w-screen bg-quite-blue text-white">
                    <h2>
                        An error occurred!
                    </h2>
                    <h4>
                        {alert}
                    </h4>
                </div>
            )}
            <div className="bg-quite-blue rounded p-7 rounded-3">
                <h1 className="font-semibold select-none text-2xl pb-2 max-w-sm text-center text-blackbird">
                    Welcome back to <div className="text-unrailed">Derailed!</div>
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
                        Login
                    </button>
                    <div className="text-blackbird font-semibold pt-2 text-sm">
                        Don't have an account? <a href="/register" className="no-underline text-unrailed">Register</a> instead.
                    </div>
                </form>
            </div>
        </main>
    )
}