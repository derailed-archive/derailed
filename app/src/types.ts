export interface User {
    id: BigInt,
    username: string,
    display_name: string | null,
    avatar: string | null,
    flags: BigInt,
    bot: boolean,
    system: boolean
}
