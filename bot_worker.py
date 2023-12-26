from logic.fix_num import fix_num

fix_num()

from logic.worker import (
    rs,
    parse_cars, send_car, send_pdf, send_new_price,
    parse_cars_job, parse_price, update_database, reset_subs,
)
from logic.constant import WORK_PARSE_CARS_DELTA, WORK_PARSE_PRICE_DELTA

import logging

from arq import cron, run_worker, Worker


class Work(Worker):
    redis_settings = rs

    functions = [
        parse_cars,
        send_car,
        send_pdf,
        send_new_price
    ]

    cron_jobs = [

        # парсинг новых объявлений
        cron(parse_cars_job,
             hour={i for i in range(1, 24, WORK_PARSE_CARS_DELTA)},
             minute={00},
             run_at_startup=False),

        # проверка цен
        cron(parse_price,
             hour={i for i in range(1, 24, WORK_PARSE_PRICE_DELTA)},
             minute={00},
             run_at_startup=False),

        # сброс активных параметров, если кончилась подписка
        cron(reset_subs,
             hour={00},
             minute={1},
             max_tries=3,
             run_at_startup=False),

        # обновление БД и бекап
        cron(update_database,
             weekday='sun',
             hour={2},
             minute={30},
             max_tries=1,
             timeout=500,
             run_at_startup=False),
    ]


def worker():
    logging.getLogger('arq.worker')
    logging.basicConfig(
        level=logging.INFO,
        format="[%(asctime)s] [%(levelname)s] [%(lineno)d] [%(name)s] [%(message)s]",
        # filename='logs/worker.log',
        # filemode='a'
    )
    run_worker(Work)


if __name__ == "__main__":
    try:
        worker()
    except (KeyboardInterrupt, SystemExit):
        print("Worker stopped")
