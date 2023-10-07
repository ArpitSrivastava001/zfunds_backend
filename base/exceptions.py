from rest_framework.views import exception_handler
from rest_framework import status
from rest_framework.response import Response
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken, AuthenticationFailed
from rest_framework.exceptions import NotAuthenticated


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)
    if isinstance(exc, (TokenError, InvalidToken, AuthenticationFailed, NotAuthenticated)):
        return Response({
            "success": False,
            "message": exc.detail,
            "data": None
        }, status=status.HTTP_401_UNAUTHORIZED)
    return response