from django.shortcuts import render

def home(request):
    q = request.GET.get('q')
    if q:
        execute_search(q)
    return render(request, 'engine/search.html')


def execute_search(q):
    # do parallel search for 3 search engines
    print('looking for ', q)
    import grequests

    urls = [
        'https://www.google.com',
        'https://wikipedia.org',
        'https://www.duckduckgo.com'
    ]

    rs = (grequests.get(u) for u in urls)
    results = grequests.map(rs)
    for res in results:
        print(res.status_code, res.content)
    return
