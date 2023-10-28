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
    public connected: boolean = false
    private token: string | null
    private ws: WebSocket | undefined = undefined
    // private ZLIB_SUFFIX: string = '\x00\x00\xff\xff'
    // private jitterPhase: boolean = true
    private sequence: number = 0
    private hbInterval: number = 0

    constructor (token: string | null) {
        this.token = token
    }

    setToken(token: string | null) {
        this.token = token
    }

    connect() {
        if (this.connected) {
            return
        }
        this.connected = true
        this.ws = new WebSocket(import.meta.env.VITE_GATEWAY_URL)
        this.ws.onmessage = (ev) => {
            {
                // @ts-ignore
                const data: GatewayMessage = JSON.parse(ev.data)
        
                console.debug(`[WS] < [t: ${data.t}] [s: ${data.s}] [op: ${data.op}]`)
        
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
                    }, hb_interval)
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
        }
        // TODO: resumes
        this.ws.onclose = (_ev) => {
            if (this.hbInterval !== 0) {
                clearInterval(this.hbInterval)
            }

            this.ws = undefined
            this.connected = false
            this.connect()
        }
        this.ws.onerror = (_ev) => {
            console.error("[WS] >> Error with websocket Gateway occured.")
        }
    }
}