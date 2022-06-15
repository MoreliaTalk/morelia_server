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

from mod.config.instance import config_option

expiration_date = config_option.logging.expiration_date
debug_expiration_date = config_option.logging.debug_expiration_date


def add_logging(debug_status: int) -> None:
    """
    Enable logging depending on start parameter uvicorn and choice their level.
    Logging information written in .log file which contains in /log folder and
    also duplicated in the console.

    Note:
        application creates two log file contains in /log folder

            one for error level - `error.log`

            one for debug level - `debug.log`

    Examples:
        Instead of print we use

            ``logger.debug('debug message')``

            ``logger.info('info message')``

            ``logger.warning('warn message')``

            ``logger.error('error message')``

            ``logger.critical('critical message')``

    Args:
        debug_status (int, requires): where number corresponds its level

            `50 - CRITICAL`

            `40 - ERROR`

            `30 - WARNING`

            `25 - SUCCESS`

            `20 - INFO`

            `10 - DEBUG`

            `5 - TRACE`
    """

    logger.remove()
    DEBUG = True if debug_status < 20 else False

    if DEBUG:
        # We connect the output to TTY, level DEBUG
        logger.add(sys.stdout,
                   format=config_option.logging.debug,
                   level="DEBUG",
                   enqueue=True,
                   colorize=True)

        # Connect the output to a file, level DEBUG
        logger.add('log/debug.log',
                   format=config_option.logging.debug,
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
                   format=config_option.logging.info,
                   level="INFO",
                   enqueue=True,
                   colorize=True)

    # We connect the output to a file, level ERROR
    logger.add('log/error.log',
               format=config_option.logging.error,
               level="ERROR",
               backtrace=True,
               diagnose=True,
               enqueue=True,
               colorize=True,
               catch=True,
               retention=f"{expiration_date} days",
               rotation="10 MB",
               compression="zip")
