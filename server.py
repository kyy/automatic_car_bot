from aiohttp import web
from webhook import webhook
import aiohttp_jinja2
import jinja2

WEB_SERVER_HOST = "127.0.0.1"
WEB_SERVER_PORT = 8350
STATIC = 'server/static'

routes = web.RouteTableDef()


@routes.get('/')
@aiohttp_jinja2.template('index.html')
async def index(request):
    return {
        'bot_url': 'https://t.me/AutomaticCarBot',
        'bot_name': 'automatic-car-bot',
        'app': request.app,
    }


app = web.Application()

app.add_routes(routes)

app.router.add_static(f'/{STATIC}', path=STATIC, name='static')
app['static_root_url'] = STATIC

aiohttp_jinja2.setup(app, loader=jinja2.FileSystemLoader('./server/templates'))

webhook(app)

if __name__ == '__main__':
    try:
        web.run_app(app, host=WEB_SERVER_HOST, port=WEB_SERVER_PORT)
    except (KeyboardInterrupt, SystemExit):
        print("Server stopped")
