-- hosts/macos/sketchybar/lib/shell.lua
-- Robust POSIX shell escaping for SketchyBar command generation.

local shell = {}

--- Shell-quotes an arbitrary string for safe POSIX / sh execution.
-- Wraps in single quotes and safely escapes embedded single quotes.
function shell.quote(s)
  if s == nil then return "''" end
  s = tostring(s)
  return "'" .. s:gsub("'", "'\\''") .. "'"
end

return shell
