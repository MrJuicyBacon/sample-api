from aiohttp.web import Application, run_app
from handlers import users_get_handler, users_orders_handler


app = Application()

app.router.add_get(r'/users/{user_id:\d+}', users_get_handler)
app.router.add_get(r'/users/{user_id:\d+}/orders', users_orders_handler)

if __name__ == '__main__':
    run_app(app)
