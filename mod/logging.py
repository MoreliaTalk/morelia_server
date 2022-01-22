"""
    Copyright (c) 2020 - present NekrodNIK, Stepan Skriabin, rus-ai and other.
    Look at the file AUTHORS.md(located at the root of the project) to get the
    full list.

    This file is part of Morelia Server.

    Morelia Server is free software: you can redistribute it and/or modify
    it under the terms of the GNU Lesser General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    Morelia Server is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Lesser General Public License for more details.

    You should have received a copy of the GNU Lesser General Public License
    along with Morelia Server. If not, see <https://www.gnu.org/licenses/>.
"""
import sys

from loguru import logger

from admin import logs
from config import LOGGING


expiration_date = LOGGING.get('EXPIRATION_DATE')
debug_expiration_date = LOGGING.get('DEBUG_EXPIRATION_DATE')


def add_logging(debug_status: int) -> None:
    """Enables logging depending on start parameter uvicorn

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
        debug_status (int, requires):
        50 - CRITICAL;
        40 - ERROR;
        30 - WARNING;
        25 - SUCCESS;
        20 - INFO;
        10 - DEBUG;
        5 - TRACE.

    Returns:
        None
    """

    logger.remove()
    DEBUG = True if debug_status < 20 else False

    if DEBUG:
        # We connect the output to TTY, level DEBUG
        logger.add(sys.stdout,
                   format=LOGGING.get("debug"),
                   level="DEBUG",
                   enqueue=True,
                   colorize=True)

        # Connect the output to a file, level DEBUG
        logger.add('log/debug.log',
                   format=LOGGING.get("debug"),
                   level="DEBUG",
                   enqueue=True,
                   colorize=True,
                   catch=True,
                   retention=f"{debug_expiration_date} days",
                   rotation="10 MB",
                   compression="zip")
    else:
        # We connect the output to TTY, level INFO
        logger.add(sys.stdout,
                   format=LOGGING.get("info"),
                   level="INFO",
                   enqueue=True,
                   colorize=True)

    # We connect the output to a file, level ERROR
    logger.add('log/error.log',
               format=LOGGING.get("error"),
               level="ERROR",
               backtrace=True,
               diagnose=True,
               enqueue=True,
               colorize=True,
               catch=True,
               retention=f"{expiration_date} days",
               rotation="10 MB",
               compression="zip")

    logger.add(logs.loguru_handler,
               format=LOGGING.get("info"),
               level="DEBUG",
               enqueue=True,
               catch=True)
