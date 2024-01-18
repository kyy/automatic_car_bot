import logging
from django_ratelimit.decorators import ratelimit
from django.http import JsonResponse
from django.shortcuts import render
from .logic.const import BOT, FAQ
import requests
from load_env import token


def index(request):
    context = {
        'bot': BOT,
        'faqs': FAQ,
    }
    return render(request, 'home/index.html', context)


@ratelimit(key='ip', rate='3/m', method=['POST'], block=True)
def message_form(request):
    msg_succes, msg_error = ("Сообщение отправлено", "Ошибка. Повторите попытку")
    try:

        email, message = request.POST['email'], request.POST['message']

        message = f'{email}\n{message}'.replace('\n', '%0A')
        session = requests.session()
        with session.get(
                f"https://api.telegram.org/bot{token}/sendMessage?chat_id={BOT['id']}&text={message}&parse_mode=HTML") as r:
            status = r.status_code
            msg, bool_status = (msg_succes, True) if status == 200 else (msg_error, False)

            return JsonResponse(data={'success': bool_status, 'message': msg})
    except Exception as e:
        logging.error(f'<message_form> -> {e}')
        return JsonResponse(data={'success': False, 'message': msg_error})
