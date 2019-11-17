from django.db import models


class SearchHistory(models.Model):
    QUEUED = 1
    STARTED = 2
    ERROR = 3
    COMPLETED = 4
    PARTIAL_COMPLETED = 5

    QUERY_STATUS_CHOICES = [
        (QUEUED, 'Queued'),
        (STARTED, 'Started'),
        (ERROR, 'Error'),
        (COMPLETED, 'Completed'),
        (PARTIAL_COMPLETED, 'Partial'),
    ]

    query = models.TextField()
    started_at = models.DateTimeField(auto_now_add=True)
    status = models.PositiveSmallIntegerField(choices=QUERY_STATUS_CHOICES,
                                              default=QUEUED)

    @property
    def result(self):
        try:
            SearchResult.objects.filter(search=self)[0]
        except IndexError:
            return None


class SearchResult(models.Model):
    # Either we should take 3 different table for 3 searches data to store or
    # we can just make columns to store different data.
    # If we will search for all available engines everytime, its OK to store
    # the data in a single table, insert race conditions we will care using
    # cache.
    search = models.ForeignKey(SearchHistory, on_delete=models.CASCADE)
    google = models.TextField()
    duckduckgo = models.TextField()
    wikipedia = models.TextField()
    completed_at = models.DateTimeField(auto_now=True)
