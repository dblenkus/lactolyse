import os

from django.conf import settings
from django.http import HttpResponse, HttpResponseBadRequest
from django.views import View


class DownloadFileView(View):

    def get(self, request):
        if 'download' not in request.session:
            return HttpResponseBadRequest()

        download = request.session.pop('download')
        file_path = os.path.join(settings.MEDIA_ROOT, download['file_path'])

        with open(file_path, 'rb') as fn:
            response = HttpResponse(fn.read())

        response['Content-Type'] = 'application/pdf'
        response['Content-Length'] = os.path.getsize(file_path)
        response['Content-Disposition'] = 'attachment; filename="{}"'.format(download['file_name'])

        return response
