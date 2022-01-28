"""
    Copyright (c) 2021 - present NekrodNIK, Stepan Skriabin, rus-ai and other.
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
import configparser
import os


config = configparser.ConfigParser()
project_path = os.path.split(os.path.abspath(__file__))[0]
config.read(os.path.join(project_path, "config.ini"))

LOGGING = config['LOGGING']
DATABASE = config["DATABASE"]
TEMPLATES = config["TEMPLATES"]
HASH_SIZE = config["HASH_SIZE"]
SERVER_LIMIT = config["SERVER_LIMIT"]
SUPERUSER = config["SUPERUSER"]
ADMIN = config["ADMIN"]