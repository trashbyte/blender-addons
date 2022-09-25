import bpy

quickuv_obj = None
quickuv_mats = []


class QUICK_UV_CHECK_PT_panel(bpy.types.Panel):
    bl_label = "Quick UV Check"
    bl_category = "Quick UV"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"

    def draw(self, context):
        label = "Enable Quick UV Check" if quickuv_obj == None else "Disable Quick UV Check"
        self.layout.operator(QuickUvToggle.bl_idname, text=label)
        self.layout.label(text="Grid Type:")
        self.layout.prop(context.scene, 'quick_uv_selection', expand=True)


def _init():
    if 'QuickUvGrid' not in bpy.data.images:
        path = bpy.utils.user_resource('SCRIPTS') + "/addons/byte/QuickUvCheck"
        img = bpy.data.images.load(path+'/Grid.png')
        img.name = "QuickUvGrid"
        img = bpy.data.images.load(path+'/Color.png')
        img.name = "QuickUvColor"
        img = bpy.data.images.load(path+'/Valle.jpg')
        img.name = "QuickUvValle"
    
    if 'Quick UV Preview' not in bpy.data.materials:
        m = bpy.data.materials.new(name="Quick UV Preview")
        m.use_nodes = True
        tree = m.node_tree
        tree.nodes.remove(tree.nodes['Principled BSDF'])
        
        emit = tree.nodes.new('ShaderNodeEmission')
        
        tex = tree.nodes.new('ShaderNodeTexImage')
        tex.image = bpy.data.images['QuickUvGrid']
        
        tree.links.new(tree.nodes['Material Output'].inputs[0], emit.outputs[0])
        tree.links.new(emit.inputs[0], tex.outputs[0])


def _select_update(self, context):
    _init()
    img = bpy.data.images[context.scene.quick_uv_selection]
    print(img)
    bpy.data.materials['Quick UV Preview'].node_tree.nodes['Image Texture'].image = img
    context.area.tag_redraw()
    context.region.tag_redraw()


class QuickUvToggle(bpy.types.Operator):
    """Quick UV Toggle"""
    bl_idname = "view.quick_uv_toggle"
    bl_label = "Quick UV Toggle"
    
    def execute(self, context):
        _init()
        
        preview_mat = bpy.data.materials["Quick UV Preview"]
        
        global quickuv_obj
        global quickuv_mats
        
        if quickuv_obj == None:
            if bpy.context.active_object and hasattr(bpy.context.active_object.data, 'materials'):
                quickuv_obj = bpy.context.active_object
                quickuv_mats = list(quickuv_obj.data.materials)
                
                for i in range(0,len(quickuv_mats)):
                    quickuv_obj.data.materials[i] = preview_mat
        else:
            for i in range(0,len(quickuv_mats)):
                quickuv_obj.data.materials[i] = quickuv_mats[i]
            quickuv_obj = None
            quickuv_mats = []
        
        context.area.tag_redraw()
        context.region.tag_redraw()
        return {'FINISHED'}

def register():
    bpy.utils.register_class(QuickUvToggle)
    bpy.utils.register_class(QUICK_UV_CHECK_PT_panel)
    bpy.types.Scene.quick_uv_selection = bpy.props.EnumProperty(items=(('QuickUvGrid','Grid',''),('QuickUvColor','Color',''),('QuickUvValle','Valle','')),update=_select_update)


def unregister():
    del bpy.types.Scene.quick_uv_selection
    bpy.utils.unregister_class(QUICK_UV_CHECK_PT_panel)
    bpy.utils.unregister_class(QuickUvToggle)
