from django.db import models

class SearchHistory(models.Model):
    FRESH = 0
    QUEUED = 1
    STARTED = 2
    ERROR = 3
    FINISHED = 4
    PARTIAL_COMPLETED = 5

    QUERY_STATUS_CHOICES = [
        (FRESH, 'Fresh'),
        (QUEUED, 'Queued'),
        (STARTED, 'Started'),
        (ERROR, 'Error'),
        (FINISHED, 'Finished'),
        (PARTIAL_COMPLETED, 'Partial'),
    ]

    query = models.TextField()
    started_at = models.DateTimeField(auto_now_add=True)
    status = models.PositiveSmallIntegerField(choices=QUERY_STATUS_CHOICES,
                                              default=FRESH)


class SearchResult(models.Model):
    # Either we should take 3 different table for 3 searches data to store or 
    # we can just make columns to store different data.
    # If we will search for all available engines everytime, its OK to store 
    # the data in a single table, insert race conditions we will care using cache.
    search = models.ForeignKey(SearchHistory)
    google_search_result = models.TextField()
    duckduckgo_search_result = models.TextField()
    wikipedia_search_result = models.TextField()
    
