from time import time
from typing import Optional
from typing import Union

# from loguru import logger
import attr


@attr.s
class TemplateErrors:
    # хранение элементов словаря Errors в виде класса
    # который даёт возможность управления и преобразования
    # хранимых данных
    get_time = int(time())
    code: int = attr.ib(default=200)
    status: str = attr.ib(default='Ok')
    time: int = attr.ib(default=get_time)
    detail: str = attr.ib(default='successfully')


# Функция "перехватчик" ошибок в конструкции try...except.
def error_catching(code: Union[int, str],
                   add_info: Optional[str] = None) -> dict:
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
    else:
        if add_info is None:
            exception = 'Exception'
        template = TemplateErrors(code=666,
                                  status=exception,
                                  time=get_time,
                                  detail=code)
        result = attr.asdict(template)

    # logger.debug(code, result)
    return result


# Пример использования
# функция проверки делимости 'b' на 2
def func(a):
    try:
        b = int(a)
        if (b / 2) == 1:
            print('NOOO.....this is bad number!')
            return error_catching(200)
        elif (b / 2) >= 2:
            print('Good number:', b)
            return error_catching(404)
    except Exception as error:
        return error_catching(error)


# запускаем
while True:
    a = input('Input number > 5: ')
    result = func(a)
    print('Result:', result)
