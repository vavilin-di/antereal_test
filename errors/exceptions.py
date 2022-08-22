class CoordsFileNonExistentError(Exception):
    msg = 'Не удалось найти файл "{}".'


class CoordsFileReadOpenError(Exception):
    msg = 'Не удалось найти файл "{}".'


class CoordsFileWriteOpenError(Exception):
    msg = 'Не удалось найти файл "{}".'


class CoordsEntryValueError(Exception):
    msg = 'Не удалось считать значения координат в строке №{} (допущено некорректное значение).'


class CoordsEntryUnevenError(Exception):
    msg = 'Не удалось считать значения координат в строке №{} (количество координат должно быть чётным).'
