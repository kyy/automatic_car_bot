from datetime import datetime, timedelta



data_now = datetime.today().date()   # сегодняшняя дата

subscription_days = timedelta(days=900)  # купленные дни

subscription_data = data_now + subscription_days    # пишем в БД дату окончнаия

current = abs(data_now - subscription_data)   # осталось дней

if data_now > subscription_data:
    print('Подписка истекла')
else:
    print('Подписка истечет через',  str(current).replace('days', 'дней').replace('day', 'день').split(',')[0])
    print('Подписка истечет ',  subscription_data)


if __name__ == '__main__':
    pass