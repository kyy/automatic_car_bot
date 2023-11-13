from aiohttp import web
from webhook import webhook
import aiohttp_jinja2
import jinja2

WEB_SERVER_HOST = "127.0.0.1"
WEB_SERVER_PORT = 8350


routes = web.RouteTableDef()


@routes.get('/')
@aiohttp_jinja2.template('index.html')
async def index(request):
    return {'title': 'automatic-car-bot', 'surname': 'Svetlov'}


app = web.Application()

aiohttp_jinja2.setup(app, loader=jinja2.FileSystemLoader('server'))
app['static_root_url'] = 'server/static'

app.add_routes(routes)

webhook(app)


if __name__ == '__main__':
    try:
        web.run_app(app, host=WEB_SERVER_HOST, port=WEB_SERVER_PORT)
    except (KeyboardInterrupt, SystemExit):
        print("Server stopped")

