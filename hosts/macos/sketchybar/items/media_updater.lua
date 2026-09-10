-- Media player updater for SketchyBar
local config_dir = os.getenv("CONFIG_DIR") or (os.getenv("HOME") .. "/.config/sketchybar")
package.path = config_dir .. "/?.lua;" .. config_dir .. "/?/init.lua;" .. package.path

local json = require("lib.json")

local info = os.getenv("INFO")
if not info or info == "" then
  os.execute("sketchybar --set media drawing=off")
  return
end

local success, data = pcall(json.decode, info)
if not success or not data then
  os.execute("sketchybar --set media drawing=off")
  return
end

local state = data.state
local artist = data.artist or ""
local title = data.title or ""

if state == "playing" and title ~= "" then
  local label_text = title
  if artist ~= "" then
    label_text = string.format("%s – %s", artist, title)
  end

  if #label_text > 40 then
    label_text = string.sub(label_text, 1, 37) .. "..."
  end
  label_text = label_text:gsub('"', '\\"')

  local cmd = string.format(
    "sketchybar --set media icon=\"♫\" label=\"%s\" drawing=on --set front_app drawing=off",
    label_text
  )
  os.execute(cmd)
else
  os.execute("sketchybar --set media drawing=off --set front_app drawing=on")
end
