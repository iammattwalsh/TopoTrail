# code
from django.db.models.signals import post_save, pre_delete
# from django.contrib.auth.models import User
from django.dispatch import receiver
from .models import Trail

from users.models import User

import asyncio
import time

# @receiver(post_save, sender=Trail)
# async def save_trail(sender, instance, created, **kwargs):
#     async with httpx.AsyncClient() as client:
#         r = await client.get("https://httpbin.org/")
#         print(r)
#     time.sleep(5)
#     # raise Exception('!!!!!!!!!!!!!!!!!test!!!!!!!!!!!!!!!!')
#     print('!!!!!!!!!!!!!!!!!!!!!!test!!!!!!!!!!!!!!!!!!!!!!')