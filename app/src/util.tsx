import superjson from "superjson"

export function toJSON(obj: any): string {
    let { json } = superjson.serialize(obj)

    return json!.toString()
}