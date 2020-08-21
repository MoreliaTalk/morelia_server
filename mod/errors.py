from time import time


# Родительский класс
class ProtocolErrors(Exception):
    # Функция конвертирует ошибку в dict
    def to_dict(self):
        dict = {
            'code': self.code,
            'status': self.status,
            'time': int(self.get_time),
            'detail': self.detail
            }
        return dict


# Подкласс Errors
class StatusError(ProtocolErrors):
    def __init__(self):
        self.get_time = time()
        self.code = 409
        self.status = 'Error'
        self.detail = 'Bad number'
        # здесь должна вызываться стороння функция
        # записывающая информацию в лог-файл
        print('ERRORS: StatusOk')


a = input('Input number > 1: ')

try:
    b = int(a)
    if b < 1:
        print('NOOO.....this is bad number!')
        raise StatusError()
    print('Good number:', b)
except StatusError as errors:
    print(errors)
    print(errors.to_dict())
