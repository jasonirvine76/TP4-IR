from django.contrib import admin
from django.urls import path
from search_machine.views import *


urlpatterns = [
    path('ask/', ask),
]