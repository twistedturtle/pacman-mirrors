TEST_FILE = "core.db.tar.gz"
# http constants
URL_MIRROR_JSON = "https://repo.manjaro.org/mirrors.json"
URL_STATUS_JSON = "https://repo.manjaro.org/status.json"
# etc
CONFIG_FILE = "tests/mock/etc/pacman-mirrors.conf"
MIRROR_LIST = "tests/mock/etc/mirrorlist"
# pacman-mirrors
WORK_DIR = "tests/mock/var"
CUSTOM_FILE = f"{WORK_DIR}/custom-mirrors.json"
MIRROR_FILE = f"{WORK_DIR}/mirrors.json"
STATUS_FILE = f"{WORK_DIR}/status.json"
# repo constants
BRANCHES = ("stable", "testing", "unstable")
ARM_BRANCHES = ("arm-stable", "arm-testing", "arm-unstable")
PROTOCOLS = ("https", "http", "ftp")
METHODS = ("rank", "random")
SSL = ("True", "False")
REPO_ARCH = "/$repo/$arch"
# special cases
TEST_CMD = "pacman-mirrors "
