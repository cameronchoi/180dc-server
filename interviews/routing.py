from django.conf.urls import url
from . import ws

websocket_urlpatterns = [
    url('ws/interview_data_stream', ws.InterviewDataConsumer.as_asgi()),
]
