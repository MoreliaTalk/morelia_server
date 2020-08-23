from time import time
from typing import Optional
from typing import Union

from loguru import logger
import attr


@attr.s
class TemplateErrors:
    """Template of class intended for storage of attributes 'Errors' object.
    When creating an instance, any passed value to e'detail' attribute
    is converted to the 'str' type.
    """
    code: int = attr.ib()
    status: str = attr.ib()
    time: int = attr.ib()
    detail: str = attr.ib(converter=str)


def error_catching(code: Union[int, str],
                   add_info: Optional[str] = None) -> dict:
    """Function catches errors in the "try...except" content.
    Result is 'dict' with information about the code, status,
    time and detailed description of the error that has occurred.
    For errors like Exception and other unrecognized errors,
    code "520" and status "Unknown Error" are used.
    Function also automatically logs the error.

    Args:
        code (Union[int, str]): Error code or type and exception description.
        add_info (Optional[str], optional): Additional information to be added.
                                            The 'Exception' field is not used
                                            for exceptions. Defaults to None.

    Returns:
        dict: returns 'dict' according to the protocol,
                like: {
                    'code': 200,
                    'status': 'Ok',
                    'time': 123456545,
                    'detail': 'successfully'
                    }


    """
    dict_all_errors = {
        '200': {
            'code': 200,
            'status': 'OK',
            'detail': 'successfully'
            },
        '201': {
            'code': 201,
            'status': 'Created',
            'detail': 'Created'
            },
        '202': {
            'code': 202,
            'status': 'Accepted',
            'detail': 'Accepted'
            },
        '400': {
            'code': 400,
            'status': 'Bad Request',
            'detail': 'Bad Request'
            },
        '401': {
            'code': 401,
            'status': 'Unauthorized',
            'detail': 'Unauthorized'
            },
        '403': {
            'code': 403,
            'status': 'Forbidden',
            'detail': 'Forbidden'
            },
        '404': {
            'code': 404,
            'status': 'Not Found',
            'detail': 'Not Found'
            },
        '405': {
            'code': 405,
            'status': 'Method Not Allowed',
            'detail': 'Method Not Allowed'
            },
        '408': {
            'code': 408,
            'status': 'Request Timeout',
            'detail': 'Request Timeout'
            },
        '415': {
            'code': 415,
            'status': 'Unsupported Media Type',
            'detail': 'Unsupported Media Type'
            },
        '417': {
            'code': 417,
            'status': 'Expectation Failed',
            'detail': 'Expectation Failed'
            },
        '426': {
            'code': 426,
            'status': 'Upgrade Required',
            'detail': 'Upgrade Required'
            },
        '429': {
            'code': 429,
            'status': 'Too Many Requests',
            'detail': 'Too Many Requests'
            },
        '499': {
            'code': 499,
            'status': 'Client Closed Request',
            'detail': 'Client Closed Request'
            },
        '500': {
            'code': 500,
            'status': 'Internal Server Error',
            'detail': 'Internal Server Error'
            },
        '503': {
            'code': 503,
            'status': 'Service Unavailable',
            'detail': 'Service Unavailable'
            },
        '526': {
            'code': 526,
            'status': 'Invalid SSL Certificate',
            'detail': 'Invalid SSL Certificate'
            },
        }

    get_time = int(time())

    code_list = (200, 201, 202, 400, 401,
                 403, 404, 405, 408, 415,
                 417, 426, 429, 499, 500,
                 503, 526)
    if code in code_list:
        if add_info is None:
            add_info = dict_all_errors[str(code)]['detail']
        template = TemplateErrors(code=code,
                                  status=dict_all_errors[str(code)]['status'],
                                  time=get_time,
                                  detail=add_info)
        result = attr.asdict(template)
        if code in (200, 201, 202):
            logger.info(f"errors code: {code}, errors result: {result}")
        else:
            logger.debug(f"errors code: {code}, errors result: {result}")
    else:
        template = TemplateErrors(code=520,
                                  status='Unknown Error',
                                  time=get_time,
                                  detail=code)
        result = attr.asdict(template)
        logger.error(f"errors code: {code}, errors result: {result}")

    return result
