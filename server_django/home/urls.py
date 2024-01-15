from django.urls import path
from .views import index, message_form, web_hook

urlpatterns = [
    path('', index, name='index'),
    path('submit_message', message_form, name='message_form'),
    path('web_hook', web_hook, name='web_hook'),
]
