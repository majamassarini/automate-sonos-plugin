# Agent guidelines

## Code style

- Prefer functions and methods with few, explicitly named and typed
  parameters. Do not use `**kwargs` (or `*args`) to accept optional
  aliases or loosely shaped input.
- Do not handle multiple field names for the same value (e.g. `value` vs
  `volume`). Each message shape has exactly one field name.
- When a new message shape or behaviour is needed, create a new class
  (a new `Command` / `Trigger` with its own `ACTION` and `Msg`) instead of
  making an existing class or `action` function accept more variants.
- Keep the `Gateway.get_action` dispatch one branch per command class,
  each calling that command's `action` with its well-defined fields.
