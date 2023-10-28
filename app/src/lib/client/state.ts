import { makeAutoObservable } from "mobx"
import Gateway from "./gateway"
import HTTPClient from "./http"

class State {
    public gateway: Gateway
    public http: HTTPClient

    constructor() {
        (window as any)["state"] = this

        console.log('opened state')
        makeAutoObservable(this)
        this.gateway = new Gateway(null)
        this.http = new HTTPClient(null)
    }

    setToken(token: string) {
        this.gateway.setToken(token)
        this.http.setToken(token)
    }
}

export default function getState(): State {
    const state = (window as any)["state"]

    if (state === undefined) {
        return new State()
    } else {
        return state
    }
}