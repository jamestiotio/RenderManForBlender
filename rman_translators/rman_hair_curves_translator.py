from .rman_translator import RmanTranslator
from ..rfb_utils import transform_utils
from ..rfb_utils import scenegraph_utils
from ..rfb_utils.timer_utils import time_this
from ..rfb_logger import rfb_log
from ..rman_sg_nodes.rman_sg_haircurves import RmanSgHairCurves
from mathutils import Vector
import math
import bpy    
import numpy as np

class BlHair:

    def __init__(self):        
        self.points = []
        self.vertsArray = []
        self.nverts = 0
        self.hair_width = []
        self.index = []
        self.bl_hair_attributes = dict()

class BlHairAttribute:

    def __init__(self):
        self.rman_type = ''
        self.rman_name = ''
        self.rman_detail = None
        self.array_len = -1
        self.values = []

class RmanHairCurvesTranslator(RmanTranslator):

    def __init__(self, rman_scene):
        super().__init__(rman_scene)
        self.bl_type = 'CURVES'  

    def export(self, ob, db_name):

        sg_node = self.rman_scene.sg_scene.CreateGroup(db_name)
        rman_sg_hair = RmanSgHairCurves(self.rman_scene, sg_node, db_name)

        return rman_sg_hair

    def clear_children(self, ob, rman_sg_hair):
        if rman_sg_hair.sg_node:
            for c in [ rman_sg_hair.sg_node.GetChild(i) for i in range(0, rman_sg_hair.sg_node.GetNumChildren())]:
                rman_sg_hair.sg_node.RemoveChild(c)
                self.rman_scene.sg_scene.DeleteDagNode(c)     
                rman_sg_hair.sg_curves_list.clear()   

    def export_deform_sample(self, rman_sg_hair, ob, time_sample):
        curves = self._get_strands_(ob)
        for i, bl_curve in enumerate(curves):
            curves_sg = rman_sg_hair.sg_curves_list[i]
            if not curves_sg:
                continue
            primvar = curves_sg.GetPrimVars()

            primvar.SetPointDetail(self.rman_scene.rman.Tokens.Rix.k_P, bl_curve.points, "vertex", time_sample)  
            curves_sg.SetPrimVars(primvar)

    def update(self, ob, rman_sg_hair):
        if rman_sg_hair.sg_node:
            if rman_sg_hair.sg_node.GetNumChildren() > 0:
                self.clear_children(ob, rman_sg_hair)

        curves = self._get_strands_(ob)
        if not curves:
            return

        for i, bl_curve in enumerate(curves):
            curves_sg = self.rman_scene.sg_scene.CreateCurves("%s-%d" % (rman_sg_hair.db_name, i))
            curves_sg.Define(self.rman_scene.rman.Tokens.Rix.k_cubic, "nonperiodic", "catmull-rom", len(bl_curve.vertsArray), len(bl_curve.points))
            primvar = curves_sg.GetPrimVars()                  
            primvar.SetPointDetail(self.rman_scene.rman.Tokens.Rix.k_P, bl_curve.points, "vertex")

            primvar.SetIntegerDetail(self.rman_scene.rman.Tokens.Rix.k_Ri_nvertices, bl_curve.vertsArray, "uniform")
            index_nm = 'index'
            primvar.SetIntegerDetail(index_nm, bl_curve.index, "uniform")

            width_detail = "vertex" 
            primvar.SetFloatDetail(self.rman_scene.rman.Tokens.Rix.k_width, bl_curve.hair_width, width_detail)
            
            for nm, hair_attr in bl_curve.bl_hair_attributes.items():
                if hair_attr.rman_detail is None:
                    continue
                if hair_attr.rman_type == "float":
                    primvar.SetFloatDetail(hair_attr.rman_name, hair_attr.values, hair_attr.rman_detail)
                elif hair_attr.rman_type == "float2":
                    primvar.SetFloatArrayDetail(hair_attr.rman_name, hair_attr.values, 2, hair_attr.rman_detail)
                elif hair_attr.rman_type == "vector":
                    primvar.SetVectorDetail(hair_attr.rman_name, hair_attr.values, hair_attr.rman_detail)
                elif hair_attr.rman_type == 'color':
                    primvar.SetColorDetail(hair_attr.rman_name, hair_attr.values, hair_attr.rman_detail)
                elif hair_attr.rman_type == 'integer':
                    primvar.SetIntegerDetail(hair_attr.rman_name, hair_attr.values, hair_attr.rman_detail)
                    
            curves_sg.SetPrimVars(primvar)
            rman_sg_hair.sg_node.AddChild(curves_sg)  
            rman_sg_hair.sg_curves_list.append(curves_sg)  
        
    def get_attributes(self, ob, bl_hair_attributes):
        uv_map = ob.original.data.surface_uv_map
        for attr in ob.data.attributes:
            if attr.name.startswith('.'):
                continue
            hair_attr = None
            if attr.data_type == 'FLOAT2':
                hair_attr = BlHairAttribute()
                hair_attr.rman_name = attr.name
                if attr.name == uv_map:
                    # rename this to be our scalpST
                    hair_attr.rman_name = 'scalpST'
                hair_attr.rman_type = 'float2'

                npoints = len(attr.data)
                values = np.zeros(npoints*2, dtype=np.float32)
                attr.data.foreach_get('vector', values)
                values = np.reshape(values, (npoints, 2))
                hair_attr.values = values.tolist()

            elif attr.data_type == 'FLOAT_VECTOR':
                hair_attr = BlHairAttribute()
                hair_attr.rman_name = attr.name
                hair_attr.rman_type = 'vector'

                npoints = len(attr.data)
                values = np.zeros(npoints*3, dtype=np.float32)
                attr.data.foreach_get('vector', values)
                values = np.reshape(values, (npoints, 3))
                hair_attr.values = values.tolist()
            
            elif attr.data_type in ['BYTE_COLOR', 'FLOAT_COLOR']:
                hair_attr = BlHairAttribute()
                hair_attr.rman_name = attr.name
                if attr.name == 'color':
                    hair_attr.rman_name = 'Cs'
                hair_attr.rman_type = 'color'

                npoints = len(attr.data)
                values = np.zeros(npoints*4, dtype=np.float32)
                attr.data.foreach_get('color', values)
                values = np.reshape(values, (npoints, 4))
                hair_attr.values .extend(values[0:, 0:3].tolist())

            elif attr.data_type == 'FLOAT':
                hair_attr = BlHairAttribute()
                hair_attr.rman_name = attr.name
                hair_attr.rman_type = 'float'
                hair_attr.array_len = -1

                npoints = len(attr.data)
                values = np.zeros(npoints, dtype=np.float32)
                attr.data.foreach_get('value', values)
                hair_attr.values = values.tolist()                          
            elif attr.data_type in ['INT8', 'INT']:
                hair_attr = BlHairAttribute()
                hair_attr.rman_name = attr.name
                hair_attr.rman_type = 'integer'
                hair_attr.array_len = -1

                npoints = len(attr.data)
                values = np.zeros(npoints, dtype=np.int32)
                attr.data.foreach_get('value', values)
                hair_attr.values = values.tolist()                
            
            if hair_attr:
                bl_hair_attributes[attr.name] = hair_attr     
                if len(attr.data) == len(ob.data.points):
                    hair_attr.rman_detail = 'vertex'
                elif len(attr.data) == len(ob.data.curves):
                    hair_attr.rman_detail = 'uniform'

    def get_attributes_for_curves(self, ob, bl_hair_attributes, bl_curve, idx, fp_idx, npoints):
        for attr in ob.data.attributes:
            if attr.name.startswith('.'):
                continue
            if attr.name not in bl_hair_attributes:
                continue
            hair_attr = bl_hair_attributes[attr.name]

            hair_curve_attr = bl_curve.bl_hair_attributes.get(attr.name, BlHairAttribute())
            hair_curve_attr.rman_name = hair_attr.rman_name
            hair_curve_attr.rman_detail = hair_attr.rman_detail
            hair_curve_attr.rman_type = hair_attr.rman_type
            if hair_attr.rman_detail == "uniform":
                hair_curve_attr.values.append(hair_attr.values[idx])
            else:
                # if the detail is vertex, use the first point index
                # and npoints to get the values we need
                # we also need to duplicate the end points, like we do for P
                vals = hair_attr.values[fp_idx:fp_idx+npoints]
                vals = vals[:1] + vals + vals[-1:]
                hair_curve_attr.values.append(vals)
            bl_curve.bl_hair_attributes[attr.name] = hair_curve_attr


    @time_this
    def _get_strands_(self, ob):

        curve_sets = []
        bl_curve = BlHair()
        db = ob.data
        bl_hair_attributes = dict()
        self.get_attributes(ob, bl_hair_attributes)
        for curve in db.curves:
            if curve.points_length < 4:
                rfb_log().error("We do not support curves with only 4 control points")
                return []

            npoints = len(curve.points)
            strand_points = np.zeros(npoints*3, dtype=np.float32)
            widths = np.zeros(npoints, dtype=np.float32)
            curve.points.foreach_get('position', strand_points)
            curve.points.foreach_get('radius', widths)
            strand_points = np.reshape(strand_points, (npoints, 3))
            if np.count_nonzero(widths) == 0:
                # radius is 0. Default to 0.005
                widths.fill(0.005)
            widths = widths * 2
            strand_points = strand_points.tolist()
            widths = widths.tolist()

            
            # double the end points
            strand_points = strand_points[:1] + \
                strand_points + strand_points[-1:]

            widths = widths[:1] + widths + widths[-1:]
            
            vertsInStrand = len(strand_points)

            bl_curve.points.extend(strand_points)
            bl_curve.vertsArray.append(vertsInStrand)
            bl_curve.hair_width.extend(widths)
            bl_curve.index.append(curve.index)
            bl_curve.nverts += vertsInStrand           

            self.get_attributes_for_curves(ob, bl_hair_attributes, bl_curve, curve.index, curve.first_point_index, npoints)
               
            # if we get more than 100000 vertices, start a new BlHair.  This
            # is to avoid a maxint on the array length
            if bl_curve.nverts > 100000:
                curve_sets.append(bl_curve)
                bl_curve = BlHair()

        if bl_curve.nverts > 0:       
            curve_sets.append(bl_curve)

        return curve_sets              
            