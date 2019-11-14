from aiohttp.web import Application, run_app
from handlers import UsersGetHandler, UsersOrdersHandler, OrderHandler, ShopGetHandler


app = Application()

app.router.add_get(r'/users/{user_id:\d+}', UsersGetHandler().get_handler())
app.router.add_get(r'/users/{user_id:\d+}/orders', UsersOrdersHandler(True, True).get_handler())
app.router.add_post(r'/order', OrderHandler().get_handler())
app.router.add_get(r'/shops/{shop_id:\d+}', ShopGetHandler(True).get_handler())

if __name__ == '__main__':
    run_app(app)
