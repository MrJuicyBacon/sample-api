from aiohttp.web import Application, run_app
from handlers import users_get_handler


app = Application()

app.router.add_get(r'/users/{user_id:\d+}', users_get_handler)

if __name__ == '__main__':
    run_app(app)
