# -*- coding: utf-8 -*-

import os
import logging.config

import yaml


def setup_logging(
        default_path='settings/logging.yaml',
        default_level=logging.WARNING,
        env_key='LOG_CFG'
):
    """Setup logging configuration"""

    if not os.path.exists('log/'):
        os.mkdir('log/')

    path = default_path
    value = os.getenv(env_key, None)
    if value:
        path = value
    if os.path.exists(path):
        with open(path, 'rt') as f:
            config = yaml.safe_load(f.read())
        logging.config.dictConfig(config)
    else:
        logging.basicConfig(level=default_level)
