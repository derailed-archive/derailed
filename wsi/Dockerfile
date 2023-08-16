FROM elixir:slim as release

WORKDIR /
COPY . .

RUN apt update && apt upgrade
RUN apt install -y curl build-essential

# required for mix release deps
RUN mix local.hex --force
RUN mix local.rebar --force
# release a production version
ENV MIX_ENV=prod
RUN mix deps.get
RUN mix deps.compile
RUN mix release stack

# recopy to open new build files
FROM elixir:slim

COPY --from=release /_build/prod/rel/stack .

CMD [ "/bin/stack", "start" ]