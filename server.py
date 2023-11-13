from aiohttp import web
from webhook import webhook


WEB_SERVER_HOST = "::"
WEB_SERVER_PORT = 8350

app = web.Application()

webhook(app)


if __name__ == '__main__':
    web.run_app(app, host=WEB_SERVER_HOST, port=WEB_SERVER_PORT)
