from django.contrib import admin
from django.urls import path
from search_machine.views import *


urlpatterns = [
    path('ask/', ask),
    path('', home),
    path('result/', result),
    path('detail/<int:id>', detail, name='detail_document')
]