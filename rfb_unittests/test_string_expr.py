import unittest
import bpy
import os
import pathlib
from ..rfb_utils import string_utils, filepath_utils

class StringExprTest(unittest.TestCase):

    @classmethod
    def add_tests(self, suite):
        suite.addTest(StringExprTest('test_get_var'))
        suite.addTest(StringExprTest('test_set_var'))
        #suite.addTest(StringExprTest('test_expand_string'))
        suite.addTest(StringExprTest('test_filepath'))

    # test getvar 
    def test_get_var(self):
        self.assertEqual(string_utils.get_var('scene'), bpy.context.scene.name)

    # test set_var
    def test_set_var(self):
        string_utils.set_var('OUT', '/var/tmp')
        self.assertEqual(string_utils.get_var('OUT'), '/var/tmp')

    # test string expansion
    def test_expand_string(self):
        s = '<OUT>/<unittest>/<scene>.<f4>.<ext>'
        compare = f'/var/tmp/StringExprTest/{bpy.context.scene.name}.0001.exr'
        string_utils.set_var('OUT', '/var/tmp')
        string_utils.set_var('unittest', 'StringExprTest')
        expanded_str = string_utils.expand_string(s, display='openexr', frame=1)
        self.assertEqual(expanded_str, compare)

    # test filepath
    def test_filepath(self):
        # test whether '\' to '/'
        s = r'C:\temp\foobar\blah.txt'
        compare = 'C:/temp/foobar/blah.txt'
        s = filepath_utils.get_real_path(s)
        self.assertEqual(s, compare)

        if not bpy.data.is_saved:
            # cannot do the relative path test if scene is not saved
            return 
        
        # test relative paths with //
        bl_scene_file = bpy.data.filepath
        bl_filepath = os.path.dirname(bl_scene_file)
        compare = os.path.join(bl_filepath, 'volumes', 'foobar.txt')
        try:
            os.makedirs(os.path.join(bl_filepath, 'volumes'))
        except:
            pass
        pathlib.Path(compare).touch()
        s = r'//volumes\foobar.txt'
        s = filepath_utils.get_real_path(s)
        try:
            self.assertEqual(s, compare)
            os.remove(compare)
            os.removedirs(os.path.join(bl_filepath, 'volumes'))
        except AssertionError as e: 
            os.remove(compare)        
            os.removedirs(os.path.join(bl_filepath, 'volumes'))
            raise

        # test <blend_dir> substitution
        compare = os.path.join('<blend_dir>', 'volumes', 'foobar.txt')
        fp = os.path.join(bl_filepath, 'volumes', 'foobar.txt')
        try:
            os.makedirs(os.path.join(bl_filepath, 'volumes'))
        except:
            pass
        pathlib.Path(fp).touch()
        s = r'//volumes\foobar.txt'
        s = filepath_utils.get_token_blender_file_path(s)     
        try:
            self.assertEqual(s, compare)
            os.remove(fp)
            os.removedirs(os.path.join(bl_filepath, 'volumes'))
        except AssertionError as e: 
            os.remove(fp)           
            os.removedirs(os.path.join(bl_filepath, 'volumes'))
            raise           
