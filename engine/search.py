import json
import logging
import requests
import threading

from django.conf import settings
from django.core.cache import cache

from searchtool.celery import app
from engine.models import SearchHistory, SearchResult


logger = logging.getLogger(__name__)


class SearchType:
    GOOGLE = 'google'
    DUCKDUCKGO = 'duckduckgo'
    WIKIPEDIA = 'wikipedia'


def execute_search(q):
    # do parallel search for 3 search engines
    sh = SearchHistory.objects.create(query=q)
    logger.debug('Queued search-id: %d, looking for %s' % (sh.id, q))
    start_searching.delay(sh.id, q)
    return sh.id


def parsed_content(search_type, response):
    if search_type == SearchType.WIKIPEDIA:
        resp = json.loads(response.content)
        return resp['query']['search']
    elif search_type == SearchType.GOOGLE:
        resp = json.loads(response.content)
        return resp['query']['search']
    elif search_type == SearchType.DUCKDUCKGO:
        resp = json.loads(response.content)
        return resp['']
    return response


def save_search_data(search_id, search_type, data):
    logger.debug(
        "data saving for search id %d, type %s" %
        (search_id, search_type))

    def cache_keygen(search_type): return "%s-%d" % (search_type, search_id)
    # cache the data  to backend configured cache for an hour
    # will write to the db if all other searches also finished.
    cache.set(cache_keygen(search_type), data, 60 * 60)
    data_dict = dict([(search_type, cache.get(cache_keygen(search_type)))
                      for search_type in (SearchType.WIKIPEDIA)])  # GOOGLE, SearchType.DUCKDUCKGO, SearchType.WIKIPEDIA)]
    if all(data_dict.values()):
        # write the data to the disk now
        sr = SeachResult.objects.get(search_id=search_id)
        sr.update(data_dict)
        # update the status of the main table
        sr.search.status = 'COMPLETED'
        sr.search.save()
        sr.save()
    else:
        pass
        # it will come again till all other search completes.
    return


def google_search(search_id, q):
    params = {'key': settings.GOOGLE_CUSTOM_SEARCH_API_KEY,
              'cx': '017576662512468239146:omuauf_lfve',
              'q': q, }
    api_url = "https://www.googleapis.com/customsearch/v1"
    response = requests.get(api_url, params)
    save_search_data(
        search_id,
        SearchType.GOOGLE,
        parsed_content(
            SearchType.GOOGLE,
            response))


def duckduckgo_search(search_id, q):
    params = {'format': 'json',
              'pretty': 1,
              'q': q, }
    api_url = "https://api.duckduckgo.com/"
    response = requests.get(api_url, params)
    save_search_data(
        search_id,
        SearchType.DUCKDUCKGO,
        parsed_content(
            SearchType.DUCKDUCKGO,
            response))


def wiki_search(search_id, q):
    api_url = "https://en.wikipedia.org/w/api.php"
    params = {
        "action": "query",
        "format": "json",
        "list": "search",
        "srsearch": q,
    }
    response = requests.get(url=api_url, params=params)
    save_search_data(
        search_id,
        SearchType.WIKIPEDIA,
        parsed_content(
            SearchType.WIKIPEDIA,
            response))


@app.task(bind=True)
def start_searching(search_id, q):
    threads = []
    for func in (google_search, duckduckgo_search, wiki_search):
        t = threading.Thread(target=func, args=(search_id, q,))
        threads.append(t)
        t.start()
    for t in threads:
        t.join()
