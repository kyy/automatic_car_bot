import time
import redis

from PIL import Image, ImageChops


def check_pictures(pic1, pic2):
    pic_1 = Image.open(pic1)
    pic_2 = Image.open(pic2)

    pic_1.thumbnail((400, 300))
    pic_2.thumbnail((400, 300))

    return ImageChops.difference(pic_1, pic_2).getbbox()


redis = redis.Redis(host='127.0.0.1', port=6379, db=10)


class DublicateRomover:
    def __init__(self, tel_id, max_len_data=3):
        self.queue = []
        self.max_len_data = max_len_data  # число используемых элементов
        self.tel_id = str(tel_id)  # id телеграм пользователя
        redis.hset(self.tel_id + '_count', 'count', '0')

    def get_count(self):
        'строка счетчика'
        get_count = redis.hget(self.tel_id + '_count', 'count').decode('utf-8')
        return int(get_count)

    def get_data(self):
        cur_id, data = redis.sscan(self.tel_id + '_data')
        return data

    def delete_data(self):

        redis.hset(self.tel_id + '_count', 'count', '0')

    def push(self, val):
        if self.get_count() <= self.max_len_data:
            count = self.get_count()
            count += 1
            redis.sadd(self.tel_id + '_data', str(count), *val)
            redis.hset(self.tel_id + '_count', 'count', str(count))
        else:
            redis.delete(self.tel_id + '_data', '1')
            redis.sadd(self.tel_id + '_data', '1', *val)

    def export(self):
        pass


rem = DublicateRomover(123456)

if __name__ == '__main__':
    while True:
        for i in range(1, 100):
            pass
            time.sleep(1)
