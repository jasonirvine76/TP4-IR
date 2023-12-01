from django.shortcuts import render
import search_machine.searching_module.RealQuery as search_engine

def ask(request):
    if request.method == 'GET':
        param  = request.GET.get('query', 'elegxo meaning')
        try:
            result = search_engine.ask(param)
            context = {"my_list" : result}
            return render(request, 'my_template.html', context)
        except Exception as e:
            print(e)
