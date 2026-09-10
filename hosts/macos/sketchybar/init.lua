-- Main entry point for SketchyBar Lua configuration
local config_dir = os.getenv("CONFIG_DIR") or (os.getenv("HOME") .. "/.config/sketchybar")
package.path = config_dir .. "/?.lua;" .. config_dir .. "/?/init.lua;" .. package.path

-- 1. Configure bar and defaults
local setup_bar = require("bar")
setup_bar()

-- 2. Setup items
local setup_workspaces = require("items.workspaces")
setup_workspaces()

local setup_front_app = require("items.front_app")
setup_front_app()

local setup_media = require("items.media")
setup_media()

local setup_status = require("items.status")
setup_status()

-- 3. Force initial bar refresh
os.execute("sketchybar --update")

-- 4. Start OmniWM IPC event watcher in background if not already running
local pcheck = io.popen("pgrep -f 'omniwmctl watch.*sketchybar' 2>/dev/null")
local running_pid = pcheck and pcheck:read("*l") or nil
if pcheck then pcheck:close() end

if not running_pid or running_pid == "" then
  os.execute(string.format("nohup '%s/helpers/omniwm_watch.sh' >/dev/null 2>&1 &", config_dir))
end
