from enum import IntEnum, IntFlag


class UserFlags(IntFlag):
    staff = 1 << 0
    admin = 1 << 1
    verified = 1 << 2
    early_supporter = 1 << 3


DEFAULT_USER_FLAGS = UserFlags(0)
DEFAULT_USER_FLAGS.early_supporter = True


class ChannelTypes(IntEnum):
    CATEGORY_CHANNEL = 0
    TEXT_CHANNEL = 1


class ActivityTypes(IntEnum):
    CUSTOM_STATUS = 0


class Status(IntEnum):
    INVISIBLE = 0
    ONLINE = 1
    IDLE = 2
    DO_NOT_DISTURB = 3


class MessageFlags(IntEnum):
    WELCOME_MESSAGE = 1 << 0


class Permissions(IntEnum):
    # OWNER = -1

    ADMINISTRATOR = 1 << 0

    # management
    MANAGE_CHANNELS = 1 << 1
    MANAGE_ROLES = 1 << 2
    MANAGE_INVITES = 1 << 3
    MANAGE_CHANNEL_HISTORY = 1 << 4
    MANAGE_GUILD = 1 << 5

    # moderation
    HANDLE_BANS = 1 << 6
    HANDLE_KICKS = 1 << 7

    # viewing
    VIEW_CHANNELS = 1 << 8
    VIEW_CHANNEL_HISTORY = 1 << 9

    # creations
    CREATE_INVITES = 1 << 10
    CREATE_MESSAGES = 1 << 11


ALL_PERMISSIONS = Permissions(0)


for attr in dir(Permissions):
    val = getattr(attr)
    if isinstance(val, Permissions):
        setattr(ALL_PERMISSIONS, attr, True)
