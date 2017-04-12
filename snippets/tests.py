import json
from rest_framework import status
from rest_framework.test import APITestCase
from snippets.models import Snippet
from snippets.serializers import SnippetSerializer


class SnippetTestCase(APITestCase):
    def setUp(self):
        Snippet.objects.create(code='a = 1')
        Snippet.objects.create(code='b = 2')
        Snippet.objects.create(code='foo = "bar\n"')

    def test_get_snippet_list(self):
        """
        Test GET /snippets/
        """
        url = '/snippets/'
        response = self.client.get(url)
        snippets = Snippet.objects.all()
        serializer = SnippetSerializer(snippets, many=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(json.loads(response.content), serializer.data)

    def test_create_snippet(self):
        """
        Test POST /snippets/
        """
        url = '/snippets/'
        data = {'code': 'abc = def'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Snippet.objects.count(), 4)
        self.assertEqual(Snippet.objects.get(pk=4).code, data['code'])

    def test_get_snippet(self):
        """
        Test GET /snippets/id/
        """
        url = '/snippets/1/'
        response = self.client.get(url)
        snippet = Snippet.objects.first()
        serializer = SnippetSerializer(snippet)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(json.loads(response.content), serializer.data)

        url = '/snippets/4/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_put_snippet(self):
        """
        Test PUT /snippets/id/
        """
        url = '/snippets/1/'
        data = {'code': 'c = 3'}
        response = self.client.put(url, data, format='json')
        snippet = Snippet.objects.first()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Snippet.objects.count(), 3)
        self.assertEqual(snippet.code, data['code'])

    def test_delete_snippet(self):
        """
        Test DELETE /snippets/id/
        """
        url = '/snippets/1/'
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Snippet.objects.count(), 2)
