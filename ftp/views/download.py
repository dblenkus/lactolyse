import os

from django.http import HttpResponse, HttpResponseBadRequest
from django.views import View


class DownloadFileView(View):

    def get(self, request):
        if 'download' not in request.session:
            return HttpResponseBadRequest()

        download = request.session.pop('download')

        with open(download['file_path'], 'rb') as fn:
            response = HttpResponse(fn.read())

        response['Content-Type'] = 'application/pdf'
        response['Content-Length'] = os.path.getsize(download['file_path'])
        response['Content-Disposition'] = 'attachment; filename="{}"'.format(download['file_name'])

        return response
