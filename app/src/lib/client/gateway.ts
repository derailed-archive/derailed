import JSON from "json-bigint"
import EventEmitter from "eventemitter3"

interface GatewayMessage {
    op: number,
    s: number | undefined,
    t: string | undefined,
    d: any,
}

export default class Gateway {
    public emitter: EventEmitter = new EventEmitter()
    private token: string
    private ws: WebSocket | undefined = undefined
    // private ZLIB_SUFFIX: string = '\x00\x00\xff\xff'
    // private jitterPhase: boolean = true
    private sequence: number = 0
    private hbInterval: number = 0

    constructor (token: string) {
        this.token = token
    }

    async connect() {
        this.ws = new WebSocket(import.meta.env.VITE_GATEWAY_URL)
        this.ws.onmessage = this.onMessage
        this.ws.onerror = this.onError
    }

    // TODO: zlib compression
    async onMessage(ev: Event) {
        // @ts-ignore
        const data: GatewayMessage = JSON.parse(ev.data)

        console.debug(`[WS] < [${data}]`)

        if (data.s !== undefined) {
            console.debug(`[WS] >> Found sequence ${data.s} in message`)
            this.sequence = data.s
        }

        if (data.t !== undefined) {
            this.emitter.emit(data.t, data.d)
        }

        if (data.op == 1) {
            const hb_interval: number = data.d.heartbeat_interval

            this.hbInterval = setInterval(() => {
                console.debug("[WS] >> Sending Heartbeat")
                this.ws?.send(JSON.stringify({
                    'op': 4,
                    'd': this.sequence
                }))
            }, hb_interval / 1000)
            console.debug("[WS] >> Sending IDENTIFY")
            this.ws?.send(JSON.stringify({
                'op': 2,
                'd': {
                    'token': this.token,
                    'compress': false
                }
            }))
        }
    }

    onError(_ev: Event) {
        if (this.hbInterval !== 0) {
            clearInterval(this.hbInterval)
        }
        console.error("[WS] >> Error with websocket Gateway occured.")
    }
}