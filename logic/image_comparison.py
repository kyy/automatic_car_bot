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
        self.s = '_|_'
        self.data_name = self.tel_id + self.s
        self.count_name = self.tel_id + self.s + 'count'

    def count(self):
        try:
            count = int(r.get(self.count_name))
        except TypeError:
            count = 0
        count = 0 if count is None or count >= self.max_len_data else count
        return count

    def push(self, val: list):
        count = self.count()
        count += 1
        r.set(self.count_name, count)
        print(count)
        return r.set(self.data_name + str(count), self.s.join(str(i) for i in val))

    def render(self):
        data = []
        for i in range(1, self.max_len_data + 1):
            item = r.get(self.tel_id + self.s + str(i)).decode('UTF-8').split(self.s)
            data.append(item)
        return data


rem = CacheCarData(123456)

if __name__ == '__main__':
    print(rem.render())
    # while True:
    #     for i in range(100):
    #         rem.push([f'{i}_http:/www.av.by/1232341', f'{i}_http:/image.png/', f'{i}_115546'])
    #
    #         print('1:', r.get('123456_|_1'))
    #         print('2:', r.get('123456_|_2'))
    #         print('3:', r.get('123456_|_3'))
    #         time.sleep(0.35)
