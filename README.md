# byte's blender addons

A collection of simple addons I've made for my own use. Probably at least a little broken. Use at your own risk.

You can clone this repo into a uniquely-named folder in `AppData/Blender Foundation/Blender/3.3/scripts/addons/` (or the equivalent on your OS) to easily keep things up to date with a `git pull`. Individual modules can be enabled or disabled in the addon's preferences.

## Modules

### Bake Shader Node

Adds a "Bake Node" operator in the shader node graph, which bakes the selected node's outputs to textures, puts those textures in a node group, and replaces the original node with that group. Currently supports undoing the operator itself, but not undoing the bake operation later on. I'm planning on adding an "unfreeze" feature that replaces the original contents.

### Quick UV Check

Adds a little panel to the properties panel ("N panel") for quickly visualizing a UV grid on an object. Has three different styles of UV grid.

### Goto Panel

Very WIP. The idea is that you can press ctrl-G to open a popup with various shortcuts and display the selected one in the properties panel for quick access. Right now it's janky and hardcoded and basically useless. You'll probably want to disable this one