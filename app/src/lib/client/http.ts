import JSON from "json-bigint"

export default class HTTPClient {
    private token: string | null
    private headers: any

    constructor (token: string | null) {
        this.token = token
        this.headers = {
            'Content-Type': 'application/json',
        }
    }

    setToken(token: string) {
        this.token = token
    }

    async request(path: string, data: any) {
        let headers = this.headers
        headers.Authorization = this.token
        await fetch(
            import.meta.env.VITE_API_URL! + path,
            {
                body: JSON.stringify(data),
                headers: headers
            }
        )
    }
}