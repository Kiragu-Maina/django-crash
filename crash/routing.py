from django.urls import re_path

from . import consumers

websocket_urlpatterns = [
    re_path(r"ws/realtime/$", consumers.RealtimeUpdatesConsumer.as_asgi()),
    re_path(r"ws/real_time_updates/(?P<group_name>\w+)/$", consumers.GameConsumer.as_asgi()),
    re_path(r"ws/table_updates/$", consumers.TableUpdateConsumer.as_asgi()),
    re_path(r"ws/balance_updates/$", consumers.BalanceUpdateConsumer.as_asgi()),
    
    
    # re_path(r"ws/managingbets/$", consumers.ManagingBetsConsumer.as_asgi()),
    
    
]