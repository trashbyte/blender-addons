# TODO:
#   add inputs to node group and hook up
#   copy/move original node into group and rename to __original__
#   add unfreeze operator that takes the __original__ node back out and restores the old connections
#   change bake op wording to "freeze"

import bpy

class BakeNodeOperator(bpy.types.Operator):
    """Bakes the active node to a texture and replaces it with the texture."""
    bl_idname = "node.bake_node_operator"
    bl_label = "Bake Node"
    bl_options = {'REGISTER', 'UNDO'}

    tex_size: bpy.props.IntVectorProperty(name='Texture Size', default=(1024, 1024), min=16, max=8192, soft_min=16, soft_max=8192, step=1, size=2)
    delete_orig: bpy.props.BoolProperty(name='Delete Original?', default=False)

    @classmethod
    def poll(cls, context):
        space = context.space_data
        return space.type == 'NODE_EDITOR' and context.active_node != None

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=400)

    def draw(self, context):
        self.layout.prop(self, 'tex_size')
        self.layout.prop(self, 'delete_orig')

    def execute(self, context):
        original_engine = bpy.context.scene.render.engine
        bpy.context.scene.render.engine = 'CYCLES'

        if context.active_object == None or len(context.selected_objects) < 1:
            self.report({'ERROR'}, "Bake Node requires an object to be selected")
            return {'CANCELLED'}

        space = context.space_data
        tree = space.node_tree
        active = context.active_node
        if any(filter(lambda sck: sck.bl_rna.identifier == 'NodeSocketShader', active.outputs)):
            self.report({'ERROR'}, "Output sockets of type Shader cannot be baked")
            return {'CANCELLED'}
        
        old_material_output = None
        if len(tree.nodes['Material Output'].inputs[0].links) > 0:
            old_material_output = tree.nodes['Material Output'].inputs[0].links[0].from_socket
        emit = tree.nodes.new('ShaderNodeEmission')
        tree.links.new(tree.nodes['Material Output'].inputs[0], emit.outputs[0])
        
        group = bpy.data.node_groups.new(active.name+' (Baked)', 'ShaderNodeTree')
        group_node = tree.nodes.new("ShaderNodeGroup")
        group_node.location = active.location
        group_node.node_tree = group
        group_outputs = group.nodes.new('NodeGroupOutput')
        group_outputs.location = (300,0)
        
        for pin in active.outputs:
            if len(pin.links) < 1:
                continue
            old_targets = [t.to_socket for t in pin.links]
            for link in pin.links:
                tree.links.remove(link)
            tree.links.new(emit.inputs[0], pin)
            tex = tree.nodes.new('ShaderNodeTexImage')
            (w, h) = self.tex_size
            img = bpy.data.images.new('', w, h)
            tex.image = img
            tex.select = True
            tree.nodes.active = tex
            bpy.ops.object.bake(type='EMIT',
                                use_selected_to_active=False,
                                target='IMAGE_TEXTURES',
                                save_mode='INTERNAL',
                                use_clear=True)
            
            tree.nodes.remove(tex)
            tex = group.nodes.new('ShaderNodeTexImage')
            tex.image = img
            group.outputs.new(pin.bl_rna.identifier, pin.name)
            group.links.new(group_outputs.inputs[pin.name], tex.outputs[0])
            for socket in old_targets:
                tree.links.new(socket, group_node.outputs[pin.name])
        
        if self.delete_orig:
            tree.nodes.remove(active)
        tree.nodes.remove(emit)
        if old_material_output != None:
            tree.links.new(tree.nodes['Material Output'].inputs[0], old_material_output)
        
        bpy.context.scene.render.engine = original_engine

        return {'FINISHED'}


def menu_func(self, context):
    self.layout.operator(BakeNodeOperator.bl_idname, text=BakeNodeOperator.bl_label)


def register():
    bpy.utils.register_class(BakeNodeOperator)
    bpy.types.NODE_MT_node.append(menu_func)


def unregister():
    bpy.types.NODE_MT_node.remove(menu_func)
    bpy.utils.unregister_class(BakeNodeOperator)
