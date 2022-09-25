import bpy


addon_keymaps = []
classnames = [
    "EasyHDRI>EASYHDRI_PT_main",
    "Bagapie.bagapie_ui>BAGAPIE_PT_modifier_panel",
    "bone_selection_sets>POSE_PT_selection_sets",
    "bl_ui.space_view3d>VIEW3D_PT_view3d_properties",
    "bl_ui.space_view3d_toolbar>VIEW3D_PT_tools_object_options",
]


class GotoPropertyGroup(bpy.types.PropertyGroup):
    target_module : bpy.props.StringProperty()
    target_rna_name : bpy.props.StringProperty()
    target_label : bpy.props.StringProperty()


def draw_popup(self, context):
    for cls in bpy.types.Panel.__subclasses__():
        id = cls.__module__+">"+cls.bl_rna.name
        if id in classnames:
            label = cls.__name__
            if hasattr(cls, 'bl_label'):
                label = cls.bl_label

            category = cls.__module__
            if hasattr(cls, 'bl_category'):
                category = cls.bl_category

            btn = self.layout.operator(GotoAddonExecute.bl_idname, text="{} > {}".format(category, label), translate=False)
            btn.target_module = cls.__module__
            btn.target_rna_name = cls.bl_rna.name
            btn.target_label = label


class GotoAddonExecute(bpy.types.Operator):
    """Goto Add-on (Execute)"""
    bl_idname = "view.goto_addon_execute"
    bl_label = "Goto Add-on (Execute)"
    
    target_module : bpy.props.StringProperty()
    target_rna_name : bpy.props.StringProperty()
    target_label : bpy.props.StringProperty()
    
    def execute(self, context):
        context.scene.goto_addon_props.target_module = self.target_module
        context.scene.goto_addon_props.target_rna_name = self.target_rna_name
        context.scene.goto_addon_props.target_label = self.target_label
        bpy.context.region.tag_redraw()
        bpy.context.area.tag_redraw()
        return {'FINISHED'}


class GotoAddonSelector(bpy.types.Operator):
    """Goto Add-on (Select)"""
    bl_idname = "view.goto_addon_selector"
    bl_label = "Goto Add-on (Select)"
    
    def execute(self, context):
        self.report({'INFO'}, self.message)
        print(self.message)
        return {'FINISHED'}
 
    def invoke(self, context, event):
        context.window_manager.popup_menu(draw_popup, title = "Goto")
        return {'FINISHED'}


class GOTO_PT_panel(bpy.types.Panel):
    bl_label = "Goto"
    bl_category = "Goto"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"

    def draw(self, context):
        target_module = context.scene.goto_addon_props.target_module
        target_rna_name = context.scene.goto_addon_props.target_rna_name
        self.bl_label = context.scene.goto_addon_props.target_label
            
        for cls in bpy.types.Panel.__subclasses__():
            if cls.__module__ == target_module and cls.bl_rna.name == target_rna_name:
                cls.draw(self, context)
                break


def register():
    bpy.utils.register_class(GotoPropertyGroup)
    bpy.utils.register_class(GotoAddonExecute)
    bpy.utils.register_class(GotoAddonSelector)
    bpy.utils.register_class(GOTO_PT_panel)

    bpy.types.Scene.goto_addon_props = bpy.props.PointerProperty(type=GotoPropertyGroup)
    
    wm = bpy.context.window_manager
    # ensure key configs available (not in background mode)
    if wm.keyconfigs.addon:
        km = wm.keyconfigs.addon.keymaps.new(name='3D View', space_type='VIEW_3D')

        kmi = km.keymap_items.new('view.goto_addon_selector', 'G', 'PRESS', ctrl=True, shift=False)

        addon_keymaps.append((km, kmi))


def unregister():
    for km, kmi in reversed(addon_keymaps):
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()
    
    bpy.utils.unregister_class(GOTO_PT_panel)
    bpy.utils.unregister_class(GotoAddonSelector)
    bpy.utils.unregister_class(GotoAddonExecute)
    bpy.utils.unregister_class(GotoPropertyGroup)
