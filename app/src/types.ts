export interface User {
    id: bigint,
    username: string,
    display_name: string | null,
    avatar: string | null,
    flags: bigint,
    bot: boolean,
    system: boolean
}
