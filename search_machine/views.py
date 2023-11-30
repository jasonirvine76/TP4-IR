from django.shortcuts import render
import search_machine.searching_module.RealQuery as search_engine
def ask(request):
    # my_list = search_engine.ask("elegxo meaning")
    print(search_engine.ask("elegxo meaning"))
    my_list = [1, 2, 3]
    context = {'my_list': my_list}
    return render(request, 'my_template.html', context)
