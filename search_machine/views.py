from django.shortcuts import render
import search_machine.searching_module.RealQuery as search_engine
from search_machine.searching_module.bsbi import BSBIIndex
from search_machine.searching_module.compression import VBEPostings
from search_machine.searching_module.Ranker import Ranker


def ask(request):
    if request.method == 'GET':
        param  = request.GET.get('query', 'elegxo meaning')
        try:
            result = search_engine.ask(param)
            context = {"my_list" : result}
            return render(request, 'my_template.html', context)
        except Exception as e:
            print(e)

def bsbi(request):
    BSBI_instance = BSBIIndex(data_dir='search_machine\searching_module\data\collections',
                              postings_encoding=VBEPostings,
                              output_dir='search_machine\searching_module\data\index')
    BSBI_instance.do_indexing()

def ranker(request):
    ranker = Ranker()
    ranker.do_ranking()
