import unittest
import bpy
from ..rfb_utils import string_utils

class StringExprTest(unittest.TestCase):

    @classmethod
    def add_tests(self, suite):
        suite.addTest(StringExprTest('test_get_var'))
        suite.addTest(StringExprTest('test_set_var'))
        suite.addTest(StringExprTest('test_expand_string'))
        suite.addTest(StringExprTest('test_frame_sensitive'))

    # test getvar 
    def test_get_var(self):
        self.assertEqual(string_utils.get_var('scene'), bpy.context.scene.name)

    # test set_var
    def test_set_var(self):
        string_utils.set_var('FOOBAR', '/var/tmp')
        self.assertEqual(string_utils.get_var('FOOBAR'), '/var/tmp')

    # test string expansion
    def test_expand_string(self):
        s = '<OUT>/<unittest>/<scene>.<f4>.<ext>'
        compare = f'/var/tmp/StringExprTest/{bpy.context.scene.name}.0001.exr'
        string_utils.set_var('unittest', 'StringExprTest')
        token_dict = {'OUT': '/var/tmp'}
        expanded_str = string_utils.expand_string(s, display='openexr', frame=1, token_dict=token_dict)
        self.assertEqual(expanded_str, compare)

    # test frame sensitivity
    def test_frame_sensitive(self):
        f1 = '/path/to/foo.<f>.exr'
        f2 = '/path/to/foo.<f4>.exr'
        f3 = '/path/to/foo.<F>.exr'
        f4 = '/path/to/foo.<F4>.exr'
        f5 = '/path/to/foo.<F_NOT>.exr'

        self.assertTrue(string_utils.check_frame_sensitive(f1))
        self.assertTrue(string_utils.check_frame_sensitive(f2))
        self.assertTrue(string_utils.check_frame_sensitive(f3))
        self.assertTrue(string_utils.check_frame_sensitive(f4))
        self.assertFalse(string_utils.check_frame_sensitive(f5))
