import { Navigate } from "react-router-dom"
import getState from "../lib/client/state"
import { observer } from "mobx-react-lite"

export default observer(() => {
    const token = localStorage.getItem("token")
    if (token === null) {
        return <Navigate to="/login" />
    }

    const state = getState()

    state.setToken(token)
    state.gateway.connect()
    return (
        <main>
            <div>
                Websockets!
            </div>
        </main>
    )
})