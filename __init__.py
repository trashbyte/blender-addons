bl_info = {
    "name": "byte's blender addons",
    "author": "trashbyte",
    "version": (1, 0),
    "blender": (3, 3, 0),
    "description": "A collection of miscellaneous utilities made for my own use.",
    "warning": "Probably at least a little broken. Use at your own risk.",
    "doc_url": "https://github.com/trashbyte/blender-addons",
    "tracker_url": "https://github.com/trashbyte/blender-addons",
    "category": "Generic",
}


import bpy

from .bake_node import register as register_bake_node
from .bake_node import unregister as unregister_bake_node

from .quick_uv import register as register_quick_uv
from .quick_uv import unregister as unregister_quick_uv

from .goto import register as register_goto
from .goto import unregister as unregister_goto


enabled_modules = {
    'bake_node': False,
    'quick_uv': False,
    'goto': False,
}


class BytesAddonPreferences(bpy.types.AddonPreferences):
    bl_idname = __name__

    bake_node: bpy.props.BoolProperty(
        name="Bake Shader Node",
        default=True,
        update=(lambda s,c: update_modules()),
    )
    quick_uv: bpy.props.BoolProperty(
        name="Quick UV Checker",
        default=True,
        update=(lambda s,c: update_modules()),
    )
    goto: bpy.props.BoolProperty(
        name="Goto Panel",
        default=True,
        update=(lambda s,c: update_modules()),
    )

    def draw(self, context):
        self.layout.label(text="Enabled modules:")
        self.layout.prop(self, "bake_node")
        self.layout.prop(self, "quick_uv")
        self.layout.prop(self, "goto")


def update_modules():
    for (module, register, unregister) in [
        ('bake_node', register_bake_node, unregister_bake_node),
        ('quick_uv', register_quick_uv, unregister_quick_uv),
        ('goto', register_goto, unregister_goto),
    ]:
        pref_enable = getattr(bpy.context.preferences.addons[__package__].preferences, module)
        if pref_enable:
            if not enabled_modules[module]:
                register()
                enabled_modules[module] = True
        else:
            if enabled_modules[module]:
                unregister()
                enabled_modules[module] = False


def register():
    bpy.utils.register_class(BytesAddonPreferences)
    update_modules()


def unregister():
    bpy.utils.unregister_class(BytesAddonPreferences)
    for func in [unregister_bake_node, unregister_quick_uv, unregister_goto]:
        func()
