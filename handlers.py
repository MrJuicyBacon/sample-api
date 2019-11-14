import json
from datetime import date
from aiohttp.web import Response, HTTPNotFound
from models import Session as DbSession
from models import User, Order, OrderItem, Shop, Book, shop_book_association_table
from sqlalchemy.exc import IntegrityError

__all__ = ['UsersGetHandler', 'UsersOrdersHandler', 'OrderHandler', 'ShopGetHandler']


# Main handler class
class SampleHandler:

    def __init__(self, *args, **kwargs):
        self.session = DbSession
        self.handler = self._handler_function

    @staticmethod
    def _create_response(status=200, body=None, content_type='application/json'):
        return Response(status=status, body=json.dumps(body, separators=(',', ':')), content_type=content_type)

    # Method for getting object from model by id
    def _get_objects_from_ids(self, model_class, ids):
        model_objects = self.session.query(model_class).filter(model_class.id.in_(ids))
        objects = {}
        for model_object in model_objects:
            objects[model_object.id] = model_object
        return objects

    def get_handler(self):
        return self.handler

    def _handler_function(self, request):
        pass


# Handler for getting user data from db
class UsersGetHandler(SampleHandler):
    async def _handler_function(self, request):
        user_id = request.match_info.get('user_id')

        if user_id is not None:
            user = self.session.query(User).get(int(user_id))
            if user is None:
                raise HTTPNotFound
            user_dict = user.as_dict()
            return self._create_response(200, user_dict)
        raise HTTPNotFound


# Handler for getting orders data for specific user from db
class UsersOrdersHandler(SampleHandler):
    def __init__(self, books_as_id=True, shops_as_id=True, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._books_as_id = books_as_id
        self._shops_as_id = shops_as_id

    async def _handler_function(self, request):
        user_id = request.match_info.get('user_id')

        # Querying orders for selected user and storing their ids
        order_objects = self.session.query(Order).with_entities(Order.id, Order.reg_date)\
            .filter(Order.user_id == user_id)
        order_ids = [order_id for order_id, _ in order_objects]

        # Querying order items for selected orders and storing books and shop ids from them if needed
        order_item_objects = self.session.query(OrderItem)\
            .with_entities(OrderItem.order_id, OrderItem.book_id, OrderItem.shop_id, OrderItem.book_quantity)\
            .filter(OrderItem.order_id.in_(order_ids))
        book_ids = set()
        shop_ids = set()

        if not (self._books_as_id and self._shops_as_id):
            for order_item_object in order_item_objects:
                book_ids.add(order_item_object.book_id)
                shop_ids.add(order_item_object.shop_id)

        # Getting books and shops dicts from stored ids if needed
        books = self._get_objects_from_ids(Book, book_ids) if not self._books_as_id and len(book_ids) else None
        shops = self._get_objects_from_ids(Shop, shop_ids) if not self._shops_as_id and len(shop_ids) else None

        # Filling final orders values from previously obtained data
        orders = []
        for order in order_objects:
            temp_obj = {
                'date': order.reg_date.strftime('%Y-%m-%d'),
                'items': []
            }
            for order_item in order_item_objects:
                if order_item.order_id == order.id:
                    temp_book = {}

                    # Filling each order depending on the parameters
                    if self._books_as_id or books is None:
                        temp_book['book_id'] = order_item.book_id
                    else:
                        temp_book['book'] = books[order_item.book_id].as_dict()
                    if self._shops_as_id or shops is None:
                        temp_book['shop_id'] = order_item.shop_id
                    else:
                        temp_book['shop'] = shops[order_item.shop_id].as_dict()
                    temp_book['quantity'] = order_item.book_quantity

                    temp_obj['items'].append(temp_book)
            orders.append(temp_obj)

        return self._create_response(200, {'orders': orders})


# Handler for ordering
class OrderHandler(SampleHandler):
    async def _handler_function(self, request):
        if request.body_exists:
            # Checking possible user_id and shop_id errors and responding accordingly
            data = await request.post()
            if len(data) == 0:
                try:
                    data = await request.json()
                except json.decoder.JSONDecodeError:
                    return self._create_response(422, {'error': 'Unable to process submitted data.'})
            try:
                user_id = int(data.get('user_id'))
                if user_id < 1:
                    raise ValueError
            except (ValueError, TypeError):
                return self._create_response(400, {'error': '"user_id" parameter is in the wrong format.'})

            # Checking possible books errors and responding accordingly
            books = data.get('books')
            if books is None:
                return self._create_response(400, {'error': '"books" field is required.'})

            try:
                books_json = json.loads(books)

                # Checking if all shops from the request are present
                # and creating book_ids dict with shop ids as keys and available books as values
                shop_ids = set([int(book['shop_id']) for book in books_json])
                shops = self.session.query(shop_book_association_table).filter(
                    shop_book_association_table.c.shop_id.in_(shop_ids)
                )
                book_ids = {}
                for shop_id, book_id in shops:
                    if shop_id in book_ids:
                        book_ids[shop_id].append(book_id)
                    else:
                        book_ids[shop_id] = [book_id]
                if len(shop_ids) != len(book_ids):
                    return self._create_response(400, {'error': 'Unable to identify all of the shops.'})

                # Creating books_dict that contains shop and book ids as keys and quantity as values
                books_dict = {}
                for book in books_json:
                    if book['id'] not in book_ids[book['shop_id']]:
                        return self._create_response(400, {'error': f'Book with id={book["id"]} is not available '
                                                                    f'at the store with id={book["shop_id"]}.'})
                    quantity = int(book['quantity'])
                    if quantity < 1:
                        return self._create_response(400, {'error': '"quantity" can\'t be less than one.'})
                    shop_book_str = f"{book['shop_id']}:{book['id']}"
                    if shop_book_str not in books_dict:
                        books_dict[shop_book_str] = quantity
                    else:
                        books_dict[shop_book_str] += quantity
            except (json.decoder.JSONDecodeError, KeyError, ValueError):
                return self._create_response(400, {'error': '"books" parameter is in the wrong format.'})

            # Creating new order object
            order = Order(reg_date=date.today(), user_id=user_id)
            self.session.add(order)
            try:
                self.session.flush()
            except IntegrityError:
                return self._create_response(400, {'error': 'Some error occurred.'})

            # Creating order items objects for previously created order
            order_items = []
            for shop_book_id, book_quantity in books_dict.items():
                shop_id, book_id = shop_book_id.split(':')
                order_items.append(
                    OrderItem(order_id=order.id, book_id=book_id, shop_id=shop_id, book_quantity=book_quantity)
                )
            self.session.add_all(order_items)

            # Committing all changes to the db
            try:
                self.session.commit()
                return self._create_response(201, {'success': True})
            except IntegrityError:
                pass

        return self._create_response(500, {'error': 'Some error occurred.'})


# Handler for getting shop data from db
class ShopGetHandler(SampleHandler):
    def __init__(self, books_as_ids=True, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._books_as_ids = books_as_ids

    def _handler_function(self, request):
        shop_id = request.match_info.get('shop_id')

        shop = self.session.query(Shop).get(shop_id)
        if shop is None:
            raise HTTPNotFound

        out = shop.as_dict()
        if self._books_as_ids:
            book_ids = [book.id for book in shop.books]
            out['book_ids'] = book_ids
        else:
            books = [book.as_dict() for book in shop.books]
            out['books'] = books

        return self._create_response(200, out)
