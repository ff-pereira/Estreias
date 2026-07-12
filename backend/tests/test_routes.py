"""
    author: ffpereira
    date: 2025-11-21
"""

from tests.base_test_case import BaseTestCase

class RoutesTest(BaseTestCase):

    def test_routes(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 302)