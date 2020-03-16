import random

from locust import between, HttpLocust, TaskSet, task


def _get_all_search_strings(_file_path):
    # expecting a different search strings in each line
    return [user.strip() for user in open(_file_path).readlines()]


SEARCH_STRINGS = _get_all_search_strings('gre-barrons.txt')


def _get_random_search_text():
    return random.choice(SEARCH_STRINGS)


class SearchToolLoadTest(TaskSet):

    def on_start(self):
        pass  # as we don't need to do login now
        # self.login()

    def login(self):
        # GET login page to get csrftoken from it
        response = self.client.get('/account/login/')
        csrftoken = response.cookies['csrftoken']
        self.csrftoken = csrftoken
        # POST to login page with csrftoken
        self.client.post('/account/login/',
                         {'username': 'dummy.user', 'password': 'strong.password'},
                         headers={'X-CSRFToken': csrftoken})

    @task(10)
    def get_search(self):
        self.client.get("/?q=%s" % (_get_random_search_text()))

    @task(1)
    def get_dashboard(self):
        self.client.get("/dashboard/")


class WebsiteUser(HttpLocust):
    task_set = SearchToolLoadTest
    wait_time = between(5, 10)
