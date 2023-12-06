from django.contrib import admin
from django.urls import path
from search_machine.views import *


urlpatterns = [
    path('ask/', ask),
    path('', home),
    path('result/', result),
    path('detail/<int:id>', detail, name='detail_document'),
    path('bsbi/bsbi_page', bsbi),
    path('bsbi/do_bsbi', do_bsbi, name='do_bsbi'),
    path('ranker/ranker_page', ranker),
    path('ranker/do_ranker', do_ranker),


]