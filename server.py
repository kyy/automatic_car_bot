# from webhook import webhook
from aiohttp import web
import aiohttp_jinja2
import jinja2
from aiohttplimiter import default_keyfunc, Limiter, RateLimitExceeded
from server_fu import FAQ, BOT
from bot_config import bot
import logging

"""     autoreload: 'adev runserver server.py'    """

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] [%(lineno)d] [%(name)s] [%(message)s]",
    # filename='server.log',
    # filemode='a'
)

WEB_SERVER_HOST = "127.0.0.1"
WEB_SERVER_PORT = 8350
STATIC = 'server/static'


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
    try:
        data = await request.post()
        email, message = data['email'], data['message']
        await bot.send_message(BOT['id'], text=f'{email}\n{message}')
        logging.info(f'send message to bot >> {email}')
        return web.json_response(data={'success': True, 'message': "Сообщение отправлено"})
    except Exception as e:
        logging.error(f'<message_form> -> {e}')
        return web.json_response(data={'success': False, 'message': "Ошибка. Повторите попытку"})


app = web.Application(middlewares=[cache_control])

app.add_routes(routes)

app.router.add_static(f'/{STATIC}', path=STATIC, name='static')
app['static_root_url'] = STATIC

aiohttp_jinja2.setup(app, loader=jinja2.FileSystemLoader('./server/templates'))

# webhook(app)

if __name__ == '__main__':
    try:
        web.run_app(app, port=WEB_SERVER_PORT, host=WEB_SERVER_HOST)
    except (KeyboardInterrupt, SystemExit):
        print("Server stopped")
