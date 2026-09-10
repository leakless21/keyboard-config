-- Bar setup and global defaults
local colors = require("colors")

local function setup_bar()
  local commands = {
    -- Bar appearance
    string.format("sketchybar --bar height=32 position=top color=0x%08x border_color=0x%08x border_width=0 blur_radius=20 shadow=off sticky=on topmost=off y_offset=0 margin=0 padding_left=10 padding_right=10",
      colors.bar_bg, colors.transparent),

    -- Global item defaults
    string.format("sketchybar --default icon.font=\"JetBrainsMono Nerd Font:Bold:13.0\" label.font=\"JetBrainsMono Nerd Font:Bold:12.0\" icon.color=0x%08x label.color=0x%08x background.height=24 background.corner_radius=6 background.color=0x%08x label.padding_left=4 label.padding_right=8 icon.padding_left=8 icon.padding_right=4",
      colors.text, colors.text, colors.transparent),
  }

  for _, cmd in ipairs(commands) do
    os.execute(cmd)
  end
end

return setup_bar
