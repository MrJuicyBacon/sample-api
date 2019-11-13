import json
from aiohttp.web import Response, HTTPNotFound
from models import Session as DbSession
from models import User


async def users_get_handler(request):
    user_id = request.match_info.get('user_id')

    if user_id is not None:
        user = DbSession().query(User).get(int(user_id))
        if user is None:
            raise HTTPNotFound
        user_dict = user.as_dict()
        return Response(body=json.dumps(user_dict, separators=(',', ':')), content_type='application/json')
    raise HTTPNotFound
