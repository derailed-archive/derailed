defmodule Derailed.Payload.Ready do
  defstruct [
    :session_id,
    :user,
    :guild_ids,
    :read_states,
    :relationships
  ]
end
