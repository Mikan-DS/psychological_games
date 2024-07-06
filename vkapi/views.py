import json

import vk
import vk_api
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from vkapi.bot_config import *

vk_session = vk_api.VkApi(token=token)
api = vk_session.get_api()

@csrf_exempt
def index(request):
    if request.method == "POST":
        data = json.loads(request.body)
        if data['secret'] == secret_key:
            if data['type'] == 'confirmation':
                # confirmation_token from bot_config.py
                return HttpResponse(confirmation_token, content_type="text/plain", status=200)
            if (data['type'] == 'message_new'):# if VK server send a message
                # api = vk.API(token, v=5.5)
                user_id = data['object']['user_id']

                # token from bot_config.py
                api.messages.send(user_id = str(user_id), message = "Hello, I'm bot!", random_id = 0)
                return HttpResponse('ok', content_type="text/plain", status=200)
    else:
        return HttpResponse('see you :)')