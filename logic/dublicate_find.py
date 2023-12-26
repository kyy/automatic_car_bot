import logging

from redis import Redis


def check_dublicate(url, ccd):
    """Проверка на дублирующее объявление, возвращает True если попался дубль"""
    ccd_cache = ccd.render()
    if ccd_cache:
        for i in ccd_cache:
            if url in i:
                logging.warning(f'Найден дубль {url}')
                return True
    return False


r = Redis(host='127.0.0.1', port=6379)


class CacheCarData:

    def __init__(self, tel_id, max_len_data=5):
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
            try:
                value = r.get(self.tel_id + self.s + str(i))
                if value is not None:
                    item = value.decode('UTF-8').split(self.s)
                    data.append(item)
            except Exception as e:
                logging.warning(f'Ошибка декодирования кеша{e}')
        return data


if __name__ == '__main__':
    c = CacheCarData(1312767421)
    c.push(['54564561', '2', '5'])
    print(c.render())
