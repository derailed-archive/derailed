# Derailed

Welcome! This is the full code and non-code repository of Derailed, the "Talk Your Way" platform.

Derailed is an open, free-to-use, and modern-day application for communication via instant messaging, voice & video, along with Reddit-like forum capabilities planned for the future. Derailed is highly concurrent, designed to scale, and utilizes some of the latest stable advances in communication technology from the past few years. It is designed to be familiar, safe, and easy to use.

Derailed serves as an alternative to Discord, Reddit, and even Twitter if you prefer. We aim to blend the best aspects of both Discord and Reddit, with a stronger emphasis on Discord-like features, while also introducing original, intuitive, and speedy new features that are beneficial to *everyone*.

You have the freedom to modify, add to, and develop Derailed for yourself, as well as contribute to and enhance Derailed. The only limitation we impose is that you cannot self-host Derailed for other users.

Derailed is open to contributions and modifications, but we request that only one instance of Derailed be available to the public. To ensure this, we use the ELv2 license. You are welcome to host Derailed on your local machine, as long as you do not permit other individuals to use it.

# Repository Details

| name          | description                                                       |
| ------------- | ----------------------------------------------------------------- |
| api           | The Derailed API, core interface for communicating with Derailed. |
| gateway       | Elixir-based Derailed Gateway to real-time communication.         |
| migrations    | Derailed's SQL database migrations.                               |
| mineral       | Derailed's database library in Rust.                              |
| brew          | Rust-to-Elixir communications library. Uses gRPC.                 |

## Coming Soon

Derailed is still a project in early pre-alpha. These are tools coming soon:

| name          | description                                                       |
| ------------- | ----------------------------------------------------------------- |
| january       | Derailed's Voice Server.                                          |
| february      | Derailed's January monitoring service.                            |
| website       | Derailed's Website.                                               |
| app           | Derailed's desktop app.                                           |
| mobile        | Derailed's React Native-based cross-platform mobile app.          |
| kubes         | Kubernetes deployment configurations.                             |
| etc           | Other configuration files for tools like NGINX.                   |

# Derailed Organization

Derailed is just starting to get reorganized at the moment. We will soon be working on
our CI and further after being working on tests.

We are also *soon* going to be configuring labels (not priority at the moment.)
This means at the current moment Derailed may feel a bit disorganized outside of our codebase.

# Deploying

This is still a TODO. Derailed is a very complicated environment to run with many
languages (JavaScript, TypeScript, Rust, Elixir, etc.) using many different
tools (actix, cowboy, sqlx, jsonrs, minio, postgresql, etc.)

## Licensing

Derailed's codebase is source available, open for modification, and licensed under ELv2.
