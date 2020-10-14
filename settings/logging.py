from loguru import logger
import sys


def add_logging(debug_status: int) -> None:
    """Function enables logging depending on the start parameter uvicorn

    Instead of print we use:                       #
               logger.debug('debug message')       #
               logger.info('info message')         #
               logger.warning('warn message')      #
               logger.error('error message')       #
               logger.critical('critical message') #

    The application creates two log/ file:
               1 - error level
               2 - debug level
    The information is also duplicated in the console

    Args:
        TODO: добавить описание типов дебаг статусов
        debug_status (str, requires): ?

    Returns:
        None
    """

    logger.remove()
    debug_on = True if debug_status < 20 else False

    fmt = "{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name: ^25} | \
    {function: ^15} | line:{line: >3} | {message}"

    if debug_on:
        # We connect the output to TTY, level DEBUG
        logger.add(sys.stdout,
                   format=fmt,
                   level="DEBUG",
                   enqueue=True,
                   colorize=True)

        logger_option = logger.opt(raw=True,
                                   colors=True)
        logger_option.info(f"<blue>{'-' * 40}\n"
                           f"{' Debug mode Included ':-^40}\n"
                           f"{'-' * 40}\n</blue>")

        # Connect the output to a file, level DEBUG
        logger.add('log/debug.log',
                   format=fmt,
                   level="DEBUG",
                   enqueue=True,
                   colorize=True,
                   catch=True,
                   rotation="10 MB",
                   compression="zip")
    else:
        # We connect the output to TTY, level INFO
        logger.add(sys.stdout,
                   format=fmt,
                   level="INFO",
                   enqueue=True,
                   colorize=True)

    # We connect the output to a file, level ERROR
    logger.add('log/error.log',
               format=fmt,
               level="ERROR",
               backtrace=True,
               diagnose=True,
               enqueue=True,
               colorize=True,
               catch=True,
               rotation="10 MB",
               compression="zip")
