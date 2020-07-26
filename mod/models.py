import sqlobject as orm

# Create table in database using ORM SQLobject


class User(orm.SQLObject):
    """The class generates a table containing data
    about the user and his settings.

    Args:
        None

    Returns:
        None
    """
    # added alternateID for added class method @byUUID
    # which will return that object
    UUID = orm.IntCol(alternateID=True, unique=True, notNone=True)
    login = orm.StringCol()
    password = orm.StringCol()
    username = orm.StringCol(default=None)
    isBot = orm.BoolCol(default=False)
    authId = orm.StringCol(default=None)
    email = orm.StringCol(default=None)
    avatar = orm.BLOBCol(default=None)
    bio = orm.StringCol(default=None)
    salt = orm.StringCol(default=None)
    key = orm.StringCol(default=None)
    # Connection to the Message table
    message = orm.MultipleJoin('Message')


class Flow(orm.SQLObject):
    """The class generates a Flow table containing information
    about threads and their types (chat, channel, group).

    Args:
        None

    Returns:
        None
    """
    time = orm.IntCol(default=None)
    flowType = orm.StringCol(default=None)
    title = orm.StringCol(default=None)
    info = orm.StringCol(default=None)
    # Connection to the Message table
    message = orm.MultipleJoin('Message')


class Message(orm.SQLObject):
    """The class generates a Message table containing information
    about user messages.

    Args:
        None

    Returns:
        None
    """
    text = orm.StringCol(default=None)
    # fromUser
    # fromUserUsername
    time = orm.IntCol(default=None)
    # fromFlow
    filePicture = orm.BLOBCol(default=None)
    fileVideo = orm.BLOBCol(default=None)
    fileAudio = orm.BLOBCol(default=None)
    fileDocument = orm.BLOBCol(default=None)
    emoji = orm.StringCol(default=None)
    editedTime = orm.IntCol(default=None)
    editedStatus = orm.BoolCol(default=None)
    # replyTo = orm.StringCol(default=None)
    user = orm.ForeignKey('User')
    flow = orm.ForeignKey('Flow')


class Errors(orm.SQLObject):
    """The class generates an Errors table in which
    all types of errors are pre-stored.

    Args:
        None

    Returns:
        None
    """
    # status and code is standart HTTP status code
    status = orm.StringCol(default=None)
    code = orm.IntCol(default=None)
    detail = orm.StringCol(default=None)
