defmodule Derailed.Payload.Ready do
  defstruct [
    :session_id,
    :user,
    :guilds,
    :read_states,
    :relationships
  ]
end
