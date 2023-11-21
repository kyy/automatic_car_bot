import asyncio
import os
from aiohttp import web
import aiohttp_jinja2
import jinja2
from dotenv import load_dotenv
from server_fu import FAQ, BOT
from aiogram import Bot

load_dotenv('bot.env')
token = os.getenv('BOT_TOKEN')
bot = Bot(token=token)

WEB_SERVER_HOST = "127.0.0.1"
WEB_SERVER_PORT = 8350
STATIC = 'server/static'

routes = web.RouteTableDef()


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
    email, message = data['email'], data['message']
    try:
        await bot.send_message(BOT['id'], text=f'{email}\n{message}')
        return web.Response(text="Сообщение отправлено")
    except:
        return web.Response(text="Повторите попытку")


app = web.Application()

app.add_routes(routes)

app.router.add_static(f'/{STATIC}', path=STATIC, name='static')
app['static_root_url'] = STATIC

aiohttp_jinja2.setup(app, loader=jinja2.FileSystemLoader('./server/templates'))

if __name__ == '__main__':
    web.run_app(app)
