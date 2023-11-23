import os
import aiohttp.web_routedef
from aiohttp import web
import aiohttp_jinja2
import jinja2
from aiohttplimiter import default_keyfunc, Limiter, RateLimitExceeded
from dotenv import load_dotenv
from server_fu import FAQ, BOT
import logging

"""     autoreload: 'adev runserver server.py'    """

load_dotenv('bot.env')

BOT_TOKEN = os.getenv('BOT_TOKEN')

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] [%(lineno)d] [%(name)s] [%(message)s]",
    # filename='server.log',
    # filemode='a'
)

WEB_SERVER_HOST = "127.0.0.1"
WEB_SERVER_PORT = 8350
STATIC = 'static'


def handler_limit_response(request: web.Request, exc: RateLimitExceeded):
    # If for some reason you want to allow the request, return aiohttplimitertest.Allow().
    logging.warning('spam')
    return web.json_response(data={'success': False, 'message': "429. Слишком частые запросы"})


limiter = Limiter(keyfunc=default_keyfunc, error_handler=handler_limit_response)

routes = web.RouteTableDef()


@web.middleware
async def cache_control(request: web.Request, handler):
    response: web.Response = await handler(request)
    resource_name = request.match_info.route.name
    if resource_name and resource_name.startswith('static'):
        response.headers.setdefault('Cache-Control', 'no-cache')
    return response


@routes.get('/')
@aiohttp_jinja2.template('index.html')
async def index_page(request):
    return {
        'bot': BOT,
        'app': request.app,
        'faqs': FAQ,
    }


@routes.post('/submit_message')
@limiter.limit("5/minute")
async def message_form(request):
    msg_succes, msg_error = ("Сообщение отправлено", "Ошибка. Повторите попытку")
    try:
        data = await request.post()
        email, message = data['email'], data['message']
        message = f'{email}\n{message}'.replace('\n', '%0A')
        session = aiohttp.ClientSession()
        async with session.get(
                f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage?chat_id={BOT['id']}&text={message}&parse_mode=HTML") as r:
            status = r.status
            msg, bool_status = (msg_succes, True) if status == 200 else (msg_error, False)
            await session.close()
            return web.json_response(data={'success': bool_status, 'message': msg})
    except Exception as e:
        logging.error(f'<message_form> -> {e}')
        return web.json_response(data={'success': False, 'message': msg_error})


app = web.Application(middlewares=[cache_control])

app.add_routes(routes)

app.router.add_static(f'/{STATIC}', path=STATIC, name='static')
app['static_root_url'] = STATIC

aiohttp_jinja2.setup(app, loader=jinja2.FileSystemLoader('./templates'))

if __name__ == '__main__':
    web.run_app(app)
    web.run_app(app, ho)
