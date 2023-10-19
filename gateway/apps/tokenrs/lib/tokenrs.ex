defmodule Derailed.Token do
  use Rustler,
    otp_app: :tokenrs,
    crate: :tokenrs

  @spec get_device_id(String.t()) :: integer()
  def get_device_id(_token), do: :erlang.nif_error(:nif_not_loaded)

  @spec verify_token(String.t(), String.t()) :: boolean()
  def verify_token(_token, _password), do: :erlang.nif_error(:nif_not_loaded)
end
