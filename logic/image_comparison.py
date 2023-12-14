import time
import redis

from PIL import Image, ImageChops


def check_pictures(pic1, pic2):
    pic_1 = Image.open(pic1)
    pic_2 = Image.open(pic2)

    pic_1.thumbnail((400, 300))
    pic_2.thumbnail((400, 300))

    return ImageChops.difference(pic_1, pic_2).getbbox()


r = redis.Redis(host='127.0.0.1', port=6379, db=10)


class CacheCarData:
    def __init__(self, tel_id, max_len_data=3):
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
        count = self._count()
        count += 1
        r.set(self.count_name, count)
        return r.set(self.data_name + str(count), self.s.join(str(i) for i in val))

    def render(self):
        data = []
        for i in range(1, self.max_len_data + 1):
            item = r.get(self.tel_id + self.s + str(i)).decode('UTF-8').split(self.s)
            if item is not None:
                data.append(item)
        return data
