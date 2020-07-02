from bpy.props import PointerProperty, StringProperty, BoolProperty, \
    EnumProperty, IntProperty, FloatProperty, \
    CollectionProperty

from ...rman_utils import filepath_utils
from ...rman_utils import property_utils
from ...rfb_logger import rfb_log
from bpy.app.handlers import persistent
from ... import rman_render
from ... import rman_bl_nodes
from ...rman_bl_nodes import rman_bl_nodes_props    
from ..rman_properties_misc import RendermanLightGroup, RendermanGroup, LightLinking
from ..rman_properties_renderlayers import RendermanRenderLayerSettings
from ... import rman_config
from ...rman_config import RmanBasePropertyGroup

import bpy
import os
import sys

class RendermanSceneSettings(RmanBasePropertyGroup, bpy.types.PropertyGroup):

    rman_config_name: StringProperty(name='rman_config_name',
                                    default='rman_properties_scene')
    
    light_groups: CollectionProperty(type=RendermanLightGroup,
                                      name='Light Groups')
    light_groups_index: IntProperty(min=-1, default=-1)

    ll: CollectionProperty(type=LightLinking,
                            name='Light Links')

    # we need these in case object/light selector changes
    def reset_ll_light_index(self, context):
        self.ll_light_index = -1

    def reset_ll_object_index(self, context):
        self.ll_object_index = -1

    ll_light_index: IntProperty(min=-1, default=-1)
    ll_object_index: IntProperty(min=-1, default=-1)
    ll_light_type: EnumProperty(
        name="Select by",
        description="Select by",
        items=[('light', 'Lights', ''),
               ('group', 'Light Groups', '')],
        default='group', update=reset_ll_light_index)

    ll_object_type: EnumProperty(
        name="Select by",
        description="Select by",
        items=[('object', 'Objects', ''),
               ('group', 'Object Groups', '')],
        default='group', update=reset_ll_object_index)

    render_layers: CollectionProperty(type=RendermanRenderLayerSettings,
                                       name='Custom AOVs')


    def update_scene_solo_light(self, context):
        rr = rman_render.RmanRender.get_rman_render()        
        if rr.rman_interactive_running:
            if self.solo_light:
                rr.rman_scene_sync.update_solo_light(context)
            else:
                rr.rman_scene_sync.update_un_solo_light(context)

    solo_light: BoolProperty(name="Solo Light", update=update_scene_solo_light, default=False)

    render_selected_objects_only: BoolProperty(
        name="Only Render Selected",
        description="Render only the selected object(s)",
        default=False)

    external_animation: BoolProperty(
        name="Render Animation",
        description="Spool Animation",
        default=False)

    # Trace Sets (grouping membership)
    object_groups: CollectionProperty(
        type=RendermanGroup, name="Trace Sets")
    object_groups_index: IntProperty(min=-1, default=-1)

@persistent
def _scene_initial_groups_handler(scene):
    '''A post load handler to make sure that object_groups
    and light_groups have an initial group that contains all
    lights and objects
    '''
    scene = bpy.context.scene
    if 'collector' not in scene.renderman.object_groups.keys():
        default_group = scene.renderman.object_groups.add()
        default_group.name = 'collector'
    if 'All' not in scene.renderman.light_groups.keys():
        default_group = scene.renderman.light_groups.add()
        default_group.name = 'All'

def _add_handlers():
    if _scene_initial_groups_handler not in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.append(_scene_initial_groups_handler)

def _remove_handlers():
    if _scene_initial_groups_handler in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.remove(_scene_initial_groups_handler)


classes = [         
    RendermanSceneSettings
]           

def register():

    for cls in classes:
        cls._add_properties(cls, 'rman_properties_scene')
        bpy.utils.register_class(cls)  

    bpy.types.Scene.renderman = PointerProperty(
        type=RendermanSceneSettings, name="Renderman Scene Settings")   

    _add_handlers() 

def unregister():

    del bpy.types.Scene.renderman

    for cls in classes:
        try:
            bpy.utils.unregister_class(cls)
        except RuntimeError:
            rfb_log().debug('Could not unregister class: %s' % str(cls))
            pass

    _remove_handlers()