from django.shortcuts import render

from engine.models import SearchHistory
from engine.search import execute_search


def home(request):
    q = request.GET.get('q')
    data = {}
    if q:
        search_id = execute_search(q)
        data = {'search_id': search_id}
    return render(request, 'engine/search.html', data)


def dashboard(request):
    latest_searches = SearchHistory.objects.all().order_by('-id')[:10]
    return render(request, 'engine/dashboard.html',
                  {'latest_searches': latest_searches})
