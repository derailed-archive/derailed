defmodule State do
  defstruct [
    :session_id,
    :session_pid,
    :user_id,
    :intents,
    :sequence,
    :zlib_enabled,
    :heartbeat_interval,
    :heartbeat_ref,
    :heartbeat_cycle_finished,
    :presence,
    :compressor
  ]
end
