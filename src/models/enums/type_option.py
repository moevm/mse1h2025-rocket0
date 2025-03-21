from enum import Enum

class TypeOption(str, Enum):
    ALL = 'all'
    USERS = 'users'
    ROLES ='roles'
    CHANNELS = 'channels'