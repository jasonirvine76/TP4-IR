from django.shortcuts import render
import search_machine.searching_module.RealQuery as search_engine

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
