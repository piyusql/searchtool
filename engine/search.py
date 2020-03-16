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
    if response.status_code in (200, 201):
        resp = json.loads(response.content)
    else:
        resp = {'status_code': response.status_code,
                'message': str(response)}
    return resp


def save_search_data(search_id, search_type, data):
    logger.debug(
        "data saving for search id %d, type %s" %
        (search_id, search_type))

    def cache_keygen(search_type): return "%s-%d" % (search_type, search_id)
    # cache the data  to backend configured cache for an hour
    # will write to the db if all other searches also finished.
    cache.set(cache_keygen(search_type), data, 60 * 60)
    data_dict = dict([(search_type, cache.get(cache_keygen(search_type)))
                      for search_type in (SearchType.GOOGLE, SearchType.DUCKDUCKGO, SearchType.WIKIPEDIA)])
    if all(data_dict.values()):
        # write the data to the disk now
        sr, _ = SearchResult.objects.get_or_create(search_id=search_id)
        for key, value in data_dict.items():
            setattr(sr, key, value)
        # update the status of the main table
        sr.search.status = SearchHistory.COMPLETED
        sr.search.save()
        sr.save()
        logger.info("Search-ID-%d Completed with last execution %s" %
                    (search_id, search_type))
    else:
        logger.info("Search-ID-%d In-Progress with current execution %s" %
                    (search_id, search_type))
        # it will come again till all other search completes.
    return


def api_caller(search_type, search_id, url, params):
    try:
        response = requests.get(url, params)
    except Exception as exc:
        response = json.dumps({'status': 'error', 'message': str(exc)})
    save_search_data(
        search_id,
        search_type,
        parsed_content(
            search_type, response))


def google_search(search_id, q):
    params = {'key': settings.GOOGLE_CUSTOM_SEARCH_API_KEY,
              'cx': '017576662512468239146:omuauf_lfve',
              'q': q,
              'num': 10, }
    api_url = "https://www.googleapis.com/customsearch/v1"
    api_caller(SearchType.GOOGLE, search_id, api_url, params)


def duckduckgo_search(search_id, q):
    params = {'format': 'json',
              'pretty': 1,
              'q': q, }
    api_url = "https://api.duckduckgo.com/"
    api_caller(SearchType.DUCKDUCKGO, search_id, api_url, params)


def wiki_search(search_id, q):
    api_url = "https://en.wikipedia.org/w/api.php"
    params = {
        "action": "query",
        "format": "json",
        "list": "search",
        "srsearch": q,
    }
    api_caller(SearchType.WIKIPEDIA, search_id, api_url, params)


@app.task(bind=True)
def start_searching(self, search_id, q):
    threads = []
    SearchHistory.objects.filter(id=search_id).update(
        status=SearchHistory.STARTED)
    for func in (google_search, duckduckgo_search, wiki_search):
        t = threading.Thread(target=func, args=(search_id, q,))
        threads.append(t)
        t.start()
    for t in threads:
        t.join()
