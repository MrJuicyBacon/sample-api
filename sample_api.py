import logging
from aiohttp.web import Application, run_app
from handlers import UsersGetHandler, UsersOrdersHandler, OrderHandler, ShopGetHandler

# Logger
logger = logging.getLogger('sample_api')
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

# Console log handler
ch = logging.StreamHandler()
ch.setFormatter(formatter)
logger.addHandler(ch)

# File log handler
fh = logging.FileHandler('log.log')
fh.setFormatter(formatter)
logger.addHandler(fh)


app = Application()

app.router.add_get(r'/users/{user_id:\d+}', UsersGetHandler().get_handler())
app.router.add_get(r'/users/{user_id:\d+}/orders', UsersOrdersHandler(True, True).get_handler())
app.router.add_post(r'/order', OrderHandler().get_handler())
app.router.add_get(r'/shops/{shop_id:\d+}', ShopGetHandler(True).get_handler())

if __name__ == '__main__':
    run_app(app)
