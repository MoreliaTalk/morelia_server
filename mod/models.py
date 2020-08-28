import sqlobject as orm


# Create table in database using ORM SQLobject
class User(orm.SQLObject):
    """The class generates a table containing data
    about the user and his settings.

    Args:
        uuid (int, required):
        login (str, required):
        password (str, required):
        username (str, optional):
        isBot (bool, optional): default False
        authId (str, optional):
        email (str, optional):
        avatar (str, optional):
        bio (str, optional):
        salt (str, optional):
        key (str, optional):

    Returns:
        None
    """
    # added alternateID for added class method @byUUID
    # which will return that object
    uuid = orm.IntCol(alternateID=True, unique=True, notNone=True)
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
        flowId (int, required):
        timeCreated (int, optional):
        flowType (str, optional):
        title (str, optional):
        info (str, optional):

    Returns:
        None
    """
    flowId = orm.IntCol(alternateID=True, unique=True, notNone=True)
    timeCreated = orm.IntCol(default=None)
    flowType = orm.StringCol(default=None)
    title = orm.StringCol(default=None)
    info = orm.StringCol(default=None)
    # Connection to the Message table
    message = orm.MultipleJoin('Message')


class Message(orm.SQLObject):
    """The class generates a Message table containing information
    about user messages.

    Args:
        text (str, optional):
        time (int, optional):
        filePicture (byte, optional):
        fileVideo (byte, optional):
        fileAudio (byte, optional):
        fileDocument (byte, optional):
        emoji (str, optional):
        editedTime (int, optional):
        editedStatus (bool, optional):

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
    editedStatus = orm.BoolCol(default=False)
    # replyTo = orm.StringCol(default=None)
    user = orm.ForeignKey('User')
    flow = orm.ForeignKey('Flow')


class Errors(orm.SQLObject):
    """The class generates an Errors table in which
    all types of errors are pre-stored.

    Args:
        status (str, optional):
        code (int, optional):
        detail (str, optional):

    Returns:
        None
    """
    # status and code is standart HTTP status code
    status = orm.StringCol(default=None)
    code = orm.IntCol(default=None)
    detail = orm.StringCol(default=None)
