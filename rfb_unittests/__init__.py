import unittest
from RenderManForBlender.rfb_unittests.test_string_expr import StringExprTest
from RenderManForBlender.rfb_unittests.test_shader_nodes import ShaderNodesTest
from RenderManForBlender.rfb_unittests.test_geo import GeoTest

classes = [
    StringExprTest,
    ShaderNodesTest,
    GeoTest
]

def suite():
    suite = unittest.TestSuite()

    for cls in classes:
        cls.add_tests(suite)

    return suite

def run_rfb_unittests():
    runner = unittest.TextTestRunner(verbosity=2, failfast=True)
    test_result = runner.run(suite())

    if test_result.wasSuccessful():
        return None
    msg = ''
    for cls, err in test_result.errors:
        msg += '%s:\n' % cls.id()
        msg += '\t%s' % err
    for cls, err in test_result.failures:
        msg += '%s:\n' % cls.id()
        msg += '\t%s' % err            
    return msg

if __name__ == '__main__':
    run_rfb_unittests()