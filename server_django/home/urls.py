from django.urls import path
from .views import index, message_form

urlpatterns = [
    path('', index, name='index'),
    path('submit_message', message_form, name='message_form'),
]
