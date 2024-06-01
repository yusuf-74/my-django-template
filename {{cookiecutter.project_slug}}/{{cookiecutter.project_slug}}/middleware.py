from json import dumps

import requests
from decouple import config as env_config
from django.http import JsonResponse


def call_chat(message):
    """Google Chat incoming webhook quickstart."""
    path = f"/v1/spaces/{env_config('GOOGLE_WORKSPACE_ID')}/messages?key={env_config('GOOGLE_WORKSPACE_KEY')}&token={env_config('GOOGLE_WORKSPACE_TOKEN')}"
    message_headers = {"Content-Type": "application/json; charset=UTF-8"}
    message = {"text": message}
    requests.post('https://chat.googleapis.com' + path, headers=message_headers, data=dumps(message))


class ErrorHandlerMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def process_exception(self, request, exception):
        message = "Request: [" + str(request.method) + '] ' + str(request.build_absolute_uri()) + "\n"
        try:
            message += "SENDER: " + str(request.user.first_name) + "\n"
        except Exception as e:
            print(e)
            message += "SENDER: Anonymous\n"
        message += "Data: " + str(request.body) + "\n"
        message += "Exception: " + str(exception)
        call_chat(message)
        return JsonResponse(
            {"error": "An internal server error occurred. Our Tech team has been notified. Please try again later."},
            status=500,
        )

    def __call__(self, request):
        response = self.get_response(request)
        return response
