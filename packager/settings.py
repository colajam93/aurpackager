BUILD_ROOT_DIR = '/tmp/aurpackager'
SLACK_NOTIFICATION = False
SLACK_NOTIFICATION_URL = ''  # REQUIRED FOR SLACK_NOTIFICATION
AUR_PACKAGER_BASE_URL = ''  # REQUIRED FOR SLACK_NOTIFICATION

try:
    from packager.settings_local import *
except ImportError:
    pass
