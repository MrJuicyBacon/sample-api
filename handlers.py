import json
from datetime import date
from aiohttp.web import Response, HTTPNotFound
from models import Session as DbSession
from models import User, Order, OrderItem, Shop, Book
from sqlalchemy import func


def create_response(status=200, body=None, content_type='application/json'):
    return Response(status=status, body=json.dumps(body, separators=(',', ':')), content_type=content_type)


def get_objects_from_ids(model_class, ids):
    session = DbSession
    model_objects = session.query(model_class).filter(model_class.id.in_(ids))
    objects = {}
    for model_object in model_objects:
        objects[model_object.id] = model_object
    return objects


async def users_get_handler(request):
    user_id = request.match_info.get('user_id')

    if user_id is not None:
        user = DbSession().query(User).get(int(user_id))
        if user is None:
            raise HTTPNotFound
        user_dict = user.as_dict()
        return create_response(200, user_dict)
    raise HTTPNotFound


async def users_orders_handler(request, books_as_id=True, shops_as_id=True):
    session = DbSession
    user_id = request.match_info.get('user_id')

    order_objects = session.query(Order).with_entities(Order.id, Order.reg_date).filter(Order.user_id == user_id)
    order_ids = [order_id for order_id, _ in order_objects]

    order_item_objects = session.query(OrderItem)\
        .with_entities(OrderItem.order_id, OrderItem.book_id, OrderItem.shop_id, OrderItem.book_quantity)\
        .filter(OrderItem.order_id.in_(order_ids))
    book_ids = set()
    shop_ids = set()

    if not (books_as_id and shops_as_id):
        for order_item_object in order_item_objects:
            book_ids.add(order_item_object.book_id)
            shop_ids.add(order_item_object.shop_id)

    books = get_objects_from_ids(Book, book_ids) if not books_as_id and len(book_ids) else None
    shops = get_objects_from_ids(Shop, shop_ids) if not shops_as_id and len(shop_ids) else None

    orders = []
    for order in order_objects:
        temp_obj = {
            'date': order.reg_date.strftime('%Y-%m-%d'),
            'items': []
        }
        for order_item in order_item_objects:
            if order_item.order_id == order.id:
                temp_book = {}

                if books_as_id or books is None:
                    temp_book['book_id'] = order_item.book_id
                else:
                    temp_book['book'] = books[order_item.book_id].as_dict()
                if shops_as_id or shops is None:
                    temp_book['shop_id'] = order_item.shop_id
                else:
                    temp_book['shop'] = shops[order_item.shop_id].as_dict()
                temp_book['quantity'] = order_item.book_quantity

                temp_obj['items'].append(temp_book)
        orders.append(temp_obj)

    return create_response(200, {'orders': orders})


async def order_handler(request):
    if request.body_exists:
        data = await request.post()
        try:
            user_id = int(data.get('user_id'))
            if user_id < 1:
                raise ValueError
        except (ValueError, TypeError):
            return create_response(400, {'error': '"user_id" parameter is in the wrong format.'})

        books = data.get('books')
        if books is None:
            return create_response(400, {'error': '"user_id", "shop_id" and "books" are required.'})

        session = DbSession
        try:
            books_json = json.loads(books)

            shop_ids = set([int(book['shop_id']) for book in books_json])
            count = session.query(Shop).with_entities(func.count()).filter(Shop.id.in_(shop_ids)).scalar()
            if len(shop_ids) != count:
                return create_response(400, {'error': 'Unable to identify all of the shops.'})

            books_dict = {}
            for book in books_json:
                quantity = int(book['quantity'])
                if quantity < 1:
                    return create_response(400, {'error': '"quantity" can\'t be less than one.'})
                shop_book_str = f"{book['shop_id']}:{book['id']}"
                if shop_book_str not in books_dict:
                    books_dict[shop_book_str] = quantity
                else:
                    books_dict[shop_book_str] += quantity
        except (json.decoder.JSONDecodeError, KeyError, ValueError):
            return create_response(400, {'error': '"books" parameter is in the wrong format.'})

        order = Order(reg_date=date.today(), user_id=user_id)
        session.add(order)
        session.flush()

        order_items = []
        for shop_book_id, book_quantity in books_dict.items():
            shop_id, book_id = shop_book_id.split(':')
            order_items.append(
                OrderItem(order_id=order.id, book_id=book_id, shop_id=shop_id, book_quantity=book_quantity)
            )
        session.add_all(order_items)

        session.commit()
        return create_response(201, {'success': True})

    return create_response(500, {'error': 'Some error occurred.'})