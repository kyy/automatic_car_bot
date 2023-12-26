import logging

from redis import Redis


def check_dublicate(photo, url, ccd):
    """Проверка на дублирующее объявление, возвращает True если попался дубль"""
    ccd_cache = ccd.render()
    if ccd_cache:
        for i in ccd_cache:
            if url in i:
                return True
    return False


r = Redis(host='127.0.0.1', port=6379)


class CacheCarData:

    def __init__(self, tel_id, max_len_data=20):
        self.max_len_data = max_len_data  # число используемых элементов
        self.tel_id = str(tel_id)  # id телеграм пользователя
        self.s = '_|_'  # символ разделения
        self.data_name = self.tel_id + self.s
        self.count_name = self.tel_id + self.s + 'count'

    def _count(self):
        try:
            count = int(r.get(self.count_name))
        except TypeError:
            count = 0
        count = 0 if count is None or count >= self.max_len_data else count
        return count

    def push(self, val: list):
        """Добавляем в кеш"""
        count = self._count()
        count += 1
        r.set(self.count_name, count)
        return r.set(self.data_name + str(count), self.s.join(str(i) for i in val))

    def render(self):
        """Выводим содержимое кеша"""
        data = []
        for i in range(1, self.max_len_data + 1):

            value = r.get(self.tel_id + self.s + str(i))

            try:
                item = value.decode('UTF-8').split(self.s)
            except Exception as e:
                logging.error(f'ошибка при декодировании кеша, возможно он пуст {value=} >> {e}')
                item = None

            if item or value is not None:
                data.append(item)
        return data


if __name__ == '__main__':
    pass
