# sample-api

Simple API app example written in python that use `aiohttp` and `sqlalchemy` libraries.

## Requirements
* Required python version: 3.6+
* Dependencies: `aiohttp==3.6.2`, `SQLAlchemy==1.3.10`

## Usage
Before running, install dependencies (`pip install -r requirements.txt`)  
To create and fill the database, run `models.py` file.  
To start the app, run `simple_api.py`

### Methods
By default the app will run on port 8080.  
Available methods:
1. Get user data by id:  
&nbsp;&nbsp;-method: GET  
&nbsp;&nbsp;-url: `/users/{user_id}`  
&nbsp;&nbsp;-response: JSON serialized user object with the following fields: `id`, `name`, `surname`, `fathers_name`, `email`.

2. Get user orders by user id:  
&nbsp;&nbsp;-method: GET  
&nbsp;&nbsp;-url: `/users/{user_id}/orders`  
&nbsp;&nbsp;-response: JSON serialized `order` object with the following fields: `date`, `items`. `items` field contains the list of books, each contains `book_id`, `shop_id` and `quantity` fields.  
&nbsp;&nbsp;Note that the `book_id` and `shop_id` fields could be replaced by `book`, `shop` fields with full objects. That can be achieved by passing corresponding parameters to the `UsersOrdersHandler`.

3. Create order:  
&nbsp;&nbsp;-method: POST  
&nbsp;&nbsp;-url: `/order`  
&nbsp;&nbsp;-request body: `user_id` field with the required user id, `books` field, that contains JSON serialized string with the array of items, each of which contains `id`, `quantity` and `shop_id` fields.  
&nbsp;&nbsp;-response: JSON serialized `order` object with the following fields: `date`, `items`. `items` field contains the list of books, each contains `book_id`, `shop_id` and `quantity` fields.  

4. Get shop information by id:
&nbsp;&nbsp;-method: GET  
&nbsp;&nbsp;-url: `/shops/{shop_id}`  
&nbsp;&nbsp;-response: JSON serialized object with the following fields: `id`, `name`. `address`, `post_code`, `book_ids`. `book_ids` field contains the list of ids of the books available from the requested store.  
&nbsp;&nbsp;Note that the `book_ids` field could be replaced by `books` field with full objects. That can be achieved by passing corresponding parameters to the `ShopGetHandler`.

### Examples
Get user data by id:
```
GET /users/2
```
Response:
```json
{"id":2,"name":"Russell","surname":"Slater","fathers_name":"B.","email":"RussellBSlater@rhyta.com"}
```
---
Get user orders by user id:
```
GET /users/2/orders
```
Response:
```json
{"orders":[{"date":"2019-11-14","items":[{"book_id":2,"shop_id":5,"quantity":1},{"book_id":3,"shop_id":6,"quantity":1}]}]}
```
---
Create order:
```
POST /order
user_id:'2', books:'[{"id":2, "quantity": 1, "shop_id": 5}, {"id":1, "quantity": 1, "shop_id": 6}]'
```
Response:
```json
{"success":true}
```
---
Get shop information by id:
```
GET /shops/3
```
Response:
```json
{"id":3,"name":"Cook & Book","address":"Place du Temps Libre 1, 1200 Woluwe-Saint-Lambert, Belgium","post_code":"","book_ids":[2,7,5,3,10,4,8,6,1]}
```
