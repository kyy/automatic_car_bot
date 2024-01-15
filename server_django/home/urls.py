from django.urls import path
from .views import index, message_form, web_hook
from load_env import token

urlpatterns = [
    path('', index, name='index'),
    path('submit_message', message_form, name='message_form'),
    path(f'{token}', web_hook, name='web_hook'),
]
