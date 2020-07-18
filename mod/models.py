import sqlobject as orm

# Create table in database using ORM SQLobject


class User(orm.SQLObject):
    userID = orm.IntCol(unique=True, notNone=True)
    login = orm.StringCol(default=None)
    password = orm.StringCol()
    username = orm.StringCol()
    isBot = orm.Bool(default=False)
    autId = orm.StringCol(default=None)
    email = orm.StringCol(default=None)
    avatar = orm.BLOBCol(default=None)
    bio = orm.StringCol(default=None)


class Flow(orm.SQLObject):
    flowId = orm.IntCol(unique=True)
    time = orm.IntCol(default=None)
    flowType = orm.StringCol(default=None)
    title = orm.StringCol(default=None)
    info = orm.StringCol(default=None)


class Message(orm.SQLObject):
    messageID = orm.IntCol(unique=True)
    text = orm.StringCol(default=None)
    # fromUserId
    fromUserUsername = orm.StringCol(default=None)
    time = orm.IntCol(default=None)
    # fromChatId = orm.IntCol()
    # filePicture = orm.BLOBCol()
    # fileVideo = orm.BLOBCol()
    # fileAudio = orm.BLOBCol()
    # fileDocument = orm.BLOBCol()
    emoji = orm.StringCol(default=None)
    editedTime = orm.IntCol(default=None)
    editedStatus = orm.BoolCol(default=None)
    # replyTo


class Errors(orm.SQLObject):
    errorsId = orm.IntCol(default=None)
    time = orm.IntCol(default=None)
    status = orm.StringCol(default=None)
    code = orm.IntCol(default=None)
    detail = orm.StringCol(default=None)
