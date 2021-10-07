from .rman_translator import RmanTranslator
from ..rman_sg_nodes.rman_sg_openvdb import RmanSgOpenVDB
from ..rfb_utils import filepath_utils
from ..rfb_utils import transform_utils
from ..rfb_utils import string_utils
from ..rfb_utils import scenegraph_utils
from ..rfb_utils.envconfig_utils import envconfig
from ..rfb_logger import rfb_log
import json

class RmanOpenVDBTranslator(RmanTranslator):

    def __init__(self, rman_scene):
        super().__init__(rman_scene)
        self.bl_type = 'VOLUME' 

    def export(self, ob, db_name):

        sg_node = self.rman_scene.sg_scene.CreateVolume(db_name)
        sg_node.Define(0,0,0)
        rman_sg_openvdb = RmanSgOpenVDB(self.rman_scene, sg_node, db_name)

        return rman_sg_openvdb

    def export_deform_sample(self, rman_sg_openvdb, ob, time_sample):
        pass

    def update(self, ob, rman_sg_openvdb):
        db = ob.data
        rm = db.renderman

        primvar = rman_sg_openvdb.sg_node.GetPrimVars()
        primvar.Clear()
        bounds = transform_utils.convert_ob_bounds(ob.bound_box)
        primvar.SetFloatArray(self.rman_scene.rman.Tokens.Rix.k_Ri_Bound, string_utils.convert_val(bounds), 6)              
        if db.filepath == '':
            primvar.SetString(self.rman_scene.rman.Tokens.Rix.k_Ri_type, "box")
            rman_sg_openvdb.sg_node.SetPrimVars(primvar)   
            return

        grids = db.grids
        if not grids.is_loaded:
            if not grids.load():
                rfb_log().error("Could not load grids and metadata for volume: %s" % ob.name)
                primvar.SetString(self.rman_scene.rman.Tokens.Rix.k_Ri_type, "box")
                rman_sg_openvdb.sg_node.SetPrimVars(primvar)   
                return

        active_index = grids.active_index
        active_grid = grids[active_index]  
        if active_grid.data_type not in ['FLOAT', 'DOUBLE']:  
            rfb_log().error("Active grid is not of float type: %s" % ob.name)
            primvar.SetString(self.rman_scene.rman.Tokens.Rix.k_Ri_type, "box")
            rman_sg_openvdb.sg_node.SetPrimVars(primvar)   
            return                      

        openvdb_file = filepath_utils.get_real_path(db.filepath)
        if db.is_sequence:
            # if we have a sequence, get the current frame filepath from the grids
            openvdb_file = filepath_utils.get_real_path(grids.frame_filepath)     

        openvdb_attrs = dict()
        openvdb_attrs['filterWidth'] = getattr(rm, 'openvdb_filterwidth')
        openvdb_attrs['velocityScale'] = getattr(rm, 'openvdb_velocityscale')
        openvdb_attrs['densityMult'] = getattr(rm, 'openvdb_densitymult')
        openvdb_attrs['densityRolloff'] = getattr(rm, 'openvdb_densityrolloff')

        json_attrs = str(json.dumps(openvdb_attrs))


        primvar.SetString(self.rman_scene.rman.Tokens.Rix.k_Ri_type, "blobbydso:impl_openvdb")  
        string_args = []
        string_args.append(openvdb_file)
        string_args.append("%s:fogvolume" % active_grid.name)
        if envconfig().build_info.version() >= "24.2":
            if rm.openvdb_velocity_grid_name == '__NONE__':
                string_args.append('')
            else:
                string_args.append(rm.openvdb_velocity_grid_name)
            string_args.append(json_attrs)
        primvar.SetStringArray(self.rman_scene.rman.Tokens.Rix.k_blobbydso_stringargs, string_args, len(string_args))

        for i, grid in enumerate(grids):
            if grid.data_type in ['FLOAT', 'DOUBLE']:
                primvar.SetFloatDetail(grid.name, [], "varying")
            elif grid.data_type in ['VECTOR_FLOAT', 'VECTOR_DOUBLE', 'VECTOR_INT']:
                primvar.SetVectorDetail(grid.name, [], "varying")
            elif grid.data_type in ['INT', 'INT64', 'BOOLEAN']:
                primvar.SetIntegerDetail(grid.name, [], "varying")
            elif grid.data_type == 'STRING':
                primvar.SetStringDetail(grid.name, [], "uniform")

        rman_sg_openvdb.sg_node.SetPrimVars(primvar)  
        attrs = rman_sg_openvdb.sg_node.GetAttributes() 
        scenegraph_utils.export_vol_aggregate(self.rman_scene.bl_scene, attrs, ob)      

        attrs.SetInteger("volume:dsominmax", rm.volume_dsominmax)
        rman_sg_openvdb.sg_node.SetAttributes(attrs)           
