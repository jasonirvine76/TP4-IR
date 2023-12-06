from django.shortcuts import render
import search_machine.searching_module.RealQuery as search_engine
from django.http import HttpResponse, HttpResponseRedirect 
from django.contrib.auth.decorators import login_required
from search_machine.searching_module.bsbi import BSBIIndex
from search_machine.searching_module.compression import VBEPostings
from search_machine.searching_module.Ranker import Ranker

def ask(request):
    if request.method == 'GET':
        param  = request.GET.get('query', 'elegxo meaning')
        try:
            result = search_engine.ask(param)
            context = {"my_list" : result, "query" : param}
            return render(request, 'result_page.html', context)
        except Exception as e:
            print(e)

def home(request):
    return render(request, 'home.html')

def result(request):
    return render(request, 'result_page.html')

def detail(request, id):
    doc = search_engine.get_doc_by_id(id)
    context = {
        'content':doc
    }
    return render(request, 'detail_page.html', context)

@login_required(login_url='/search-machine/')
def bsbi(request):
    return render(request, 'bsbi_page.html')

@login_required(login_url='/search-machine/')
def do_bsbi(request):
    BSBI_instance = BSBIIndex(data_dir='search_machine\searching_module\data\collections',
                              postings_encoding=VBEPostings,
                              output_dir='search_machine\searching_module\data\index')
    BSBI_instance.do_indexing()
    return HttpResponseRedirect('/search-machine/')


@login_required(login_url='/search-machine/')
def ranker(request):
    return render(request, 'ranker_page.html')

@login_required(login_url='/search-machine/')
def do_ranker(request):
    ranker = Ranker()
    ranker.do_ranking()
    return HttpResponseRedirect('/search-machine/')


