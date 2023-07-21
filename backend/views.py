

from django.shortcuts import render
from requests import get
from rest_framework.response import Response
from rest_framework.views import APIView


class UploadData(APIView):
    def post(self, request):
        url = request.data.get('url')
        stream = get('https://disk.yandex.ru/d/7xzOIzEhnD24wQ').text
        return Response(stream)


