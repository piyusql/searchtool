from django.test import Client, TestCase


class SearchTestCase(TestCase):
    def setUp(self):
        self.query = "human intelligence"
        self.client = Client()

    def test_working_search_page(self):
        response = self.client.get('/?q=%s' % (self.query))
        # Check that the response is 200 OK.
        self.assertEqual(response.status_code, 200)
