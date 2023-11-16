from aiohttp import web
from webhook import webhook
import aiohttp_jinja2
import jinja2
from server_fu import FAQ, BOT

"""     autoreload: 'adev runserver server.py'    """

WEB_SERVER_HOST = "127.0.0.1"
WEB_SERVER_PORT = 8350
STATIC = 'server/static'

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
async def message_form(request):
    data = await request.post()
    name = data['name']
    email = data['email']
    subject = data['subject']
    message = data['message']
    print(name, message, email, subject)
    return 'Form submitted!'


app = web.Application(middlewares=[cache_control])


app.add_routes(routes)

app.router.add_static(f'/{STATIC}', path=STATIC, name='static')
app['static_root_url'] = STATIC

aiohttp_jinja2.setup(app, loader=jinja2.FileSystemLoader('./server/templates'))

# webhook(app)

if __name__ == '__main__':
    try:
        web.run_app(app, host=WEB_SERVER_HOST, port=WEB_SERVER_PORT)
    except (KeyboardInterrupt, SystemExit):
        print("Server stopped")
