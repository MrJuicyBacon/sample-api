import json
from aiohttp.web import Response, HTTPNotFound
from models import Session as DbSession
from models import User, Order, OrderItem, Shop, Book


async def users_get_handler(request):
    user_id = request.match_info.get('user_id')

    if user_id is not None:
        user = DbSession().query(User).get(int(user_id))
        if user is None:
            raise HTTPNotFound
        user_dict = user.as_dict()
        return Response(body=json.dumps(user_dict, separators=(',', ':')), content_type='application/json')
    raise HTTPNotFound


async def users_orders_handler(request):
    session = DbSession()
    user_id = request.match_info.get('user_id')

    order_objects = session.query(Order).with_entities(Order.id, Order.reg_date).filter(Order.user_id == user_id)
    order_ids = [order_id for order_id, _ in order_objects]

    order_item_objects = session.query(OrderItem)\
        .with_entities(OrderItem.order_id, OrderItem.book_id, OrderItem.shop_id)\
        .filter(OrderItem.order_id.in_(order_ids))
    book_ids = set()
    shop_ids = set()

    for _, book_id, shop_id in order_item_objects:
        book_ids.add(book_id)
        shop_ids.add(shop_id)

    book_objects = session.query(Book).filter(Book.id.in_(book_ids))
    shop_objects = session.query(Shop).filter(Shop.id.in_(shop_ids))
    books = {}
    for book_object in book_objects:
        books[book_object.id] = book_object
    shops = {}
    for shop_object in shop_objects:
        shops[shop_object.id] = shop_object

    order_items_count = {}
    order_items = []
    for order_item in order_item_objects:
        if f'{order_item.order_id}:{order_item.shop_id}:{order_item.book_id}' not in order_items_count:
            order_items.append(order_item)
            order_items_count[f'{order_item.order_id}:{order_item.shop_id}:{order_item.book_id}'] = 1
        else:
            order_items_count[f'{order_item.order_id}:{order_item.shop_id}:{order_item.book_id}'] += 1

    orders = []
    for order in order_objects:
        temp_obj = {
            'date': order.reg_date.strftime('%Y-%m-%d'),
            'items': []
        }
        for order_item in order_items:
            if order_item.order_id == order.id:
                temp_obj['items'].append({
                    'book': books[order_item.book_id].as_dict(),
                    'shop': shops[order_item.shop_id].as_dict(),
                    'quantity': order_items_count[f'{order_item.order_id}:{order_item.shop_id}:{order_item.book_id}'],
                })
        orders.append(temp_obj)

    return Response(body=json.dumps({'orders': orders}, separators=(',', ':')), content_type='application/json')
