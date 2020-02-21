RFB_ADDON_VERSION_MAJOR = 23
RFB_ADDON_VERSION_MINOR = 0
RFB_ADDON_VERSION_PATCH = 0
RFB_ADDON_VERSION = (RFB_ADDON_VERSION_MAJOR, RFB_ADDON_VERSION_MINOR, RFB_ADDON_VERSION_PATCH)
RFB_ADDON_VERSION_STRING = '%d.%d.%d' % (RFB_ADDON_VERSION_MAJOR, RFB_ADDON_VERSION_MINOR, RFB_ADDON_VERSION_PATCH)

BLENDER_SUPPORTED_VERSION_MAJOR = 2
BLENDER_SUPPORTED_VERSION_MINOR = 80
BLENDER_SUPPORTED_VERSION_PATCH = 0
BLENDER_SUPPORTED_VERSION = (BLENDER_SUPPORTED_VERSION_MAJOR, BLENDER_SUPPORTED_VERSION_MINOR, BLENDER_SUPPORTED_VERSION_PATCH)

RMAN_SUPPORTED_VERSION_MAJOR = 23
RMAN_SUPPORTED_VERSION_MINOR = 0
RMAN_SUPPORTED_VERSION_BETA = ''
RMAN_SUPPORTED_VERSION = (RMAN_SUPPORTED_VERSION_MAJOR, RMAN_SUPPORTED_VERSION_MINOR, RMAN_SUPPORTED_VERSION_BETA)
RMAN_SUPPORTED_VERSION_STRING = '%d.%d%s' % (RMAN_SUPPORTED_VERSION_MAJOR, RMAN_SUPPORTED_VERSION_MINOR, RMAN_SUPPORTED_VERSION_BETA)


RFB_ADDON_DESCRIPTION = 'RenderMan %d.%d integration' % (RMAN_SUPPORTED_VERSION_MAJOR, RMAN_SUPPORTED_VERSION_MINOR)

NODE_LAYOUT_SPLIT = 0.5