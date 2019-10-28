from django.shortcuts import render

from engine.models import SearchHistory
from engine.search import execute_search


def home(request):
    q = request.GET.get('q')
    if q:
        search_id = execute_search(q)
    return render(request, 'engine/search.html')


def dashboard(request):
    latest_searches = SearchHistory.objects.all().order_by('-id')[:10]
    return render(request, 'engine/dashboard.html', {'latest_searches': latest_searches})
