import bpy

from bpy.props import BoolProperty
from bpy.utils import register_class, unregister_class


bl_info = {
    "name": "AutoRange",
    "author": "Demian Karpunov",
    "version": (0, 2),
    "blender": (3, 1, 2),
    "location": "Timeline -> Use AutoRange",
    "description": "Automatically set frame range by active object animation",
    "warning": "",
    "doc_url": "",
    "tracker_url": "",
    "category": "Scene",
    "support": "TESTING"
}


""" LOCALS """

RANGE_UPDATE = False   # Prevents looping


class AutoRange(bpy.types.Operator):
    """Automatically set frame range with active object animation"""
    bl_idname = "scene.auto_range"
    bl_label = "Auto Range"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        # Define scene and properties
        scene = context.scene
        
        obj = context.active_object
        if not obj:
            self.report({"WARNING"}, "Active object required")
            return {"FINISHED"}
        
        anim_data = obj.animation_data
        if not anim_data or not anim_data.action:
            self.report({"WARNING"}, "Animation required")
            return {"FINISHED"}
        
        # Find action range
        action = anim_data.action
        start, end = action.frame_range

        # TODO: One key range
        self.report({"DEBUG"}, f"Frame range: {start}-{end}")
        start, end = round(start), round(end)
        
        # Set frame range
        if not all([scene.frame_start == start, scene.frame_end == end]):
            self.report({"INFO"}, f"Set frame range {start}-{end}")
            scene.frame_start = start
            scene.frame_end = end
        return {"FINISHED"}


def update_frame_range():
    context = bpy.context
    scene = context.scene
    if not scene.autorange_enabled:
        return
    
    bpy.ops.scene.auto_range("EXEC_DEFAULT")


def update_frame_range_handler(scene):
    global RANGE_UPDATE
    if RANGE_UPDATE:
        return
    
    RANGE_UPDATE = True
    update_frame_range()
    RANGE_UPDATE = False


def draw_autorange_property(self, context):
    scene = context.scene
    layout = self.layout

    # call the property
    layout.prop(scene, "autorange_enabled")


""" REGISTER """


def register():
    register_class(AutoRange)
    bpy.types.Scene.autorange_enabled = BoolProperty(
        name="Use AutoRange",
        description="AutoRange frames",
        default=False
    )
    bpy.app.handlers.depsgraph_update_pre.append(update_frame_range_handler)
    bpy.types.TIME_MT_editor_menus.append(draw_autorange_property)


def unregister():
    bpy.types.TIME_MT_editor_menus.remove(draw_autorange_property)
    bpy.app.handlers.depsgraph_update_pre.remove(update_frame_range_handler)
    del bpy.types.Scene.autorange_enabled
    unregister_class(AutoRange)


if __name__ == "__main__":
    register()
