from django.utils.translation import gettext_lazy as _
from rest_framework import status
from rest_framework.response import Response

from dj_rest_auth.views import LoginView
from dj_rest_auth.registration.views import RegisterView
from allauth.account import app_settings as allauth_account_settings
from dj_rest_auth.app_settings import api_settings


class CustomLoginView(LoginView):
    def post(self, request, *args, **kwargs):
        self.request = request
        self.serializer = self.get_serializer(data=self.request.data)
        self.serializer.is_valid(raise_exception=True)

        self.login()

        # Get the response from the parent class
        response = super().get_response()
        # Modify the response to remove 'access' and 'refresh' fields
        if "access" in response.data and "refresh" in response.data:
            del response.data["access"]
            del response.data["refresh"]
        return response


from dj_rest_auth.jwt_auth import (
    CookieTokenRefreshSerializer,
    set_jwt_access_cookie,
    set_jwt_refresh_cookie,
)


def get_custom_refresh_view():
    """Returns a Token Refresh CBV without a circular import"""
    from rest_framework_simplejwt.settings import api_settings as jwt_settings
    from rest_framework_simplejwt.views import TokenRefreshView

    class RefreshViewWithCookieSupport(TokenRefreshView):
        serializer_class = CookieTokenRefreshSerializer

        def finalize_response(self, request, response, *args, **kwargs):
            if response.status_code == status.HTTP_200_OK and "access" in response.data:
                set_jwt_access_cookie(response, response.data["access"])
                # response.data["access_expiration"] = (
                #     timezone.now() + jwt_settings.ACCESS_TOKEN_LIFETIME
                # )
                del response.data["access"]
            if (
                response.status_code == status.HTTP_200_OK
                and "refresh" in response.data
            ):
                set_jwt_refresh_cookie(response, response.data["refresh"])
                # response.data["refresh_expiration"] = (
                #     timezone.now() + jwt_settings.REFRESH_TOKEN_LIFETIME
                # )
                del response.data["refresh"]
            return super().finalize_response(request, response, *args, **kwargs)

    return RefreshViewWithCookieSupport


class CustomRegisterView(RegisterView):
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        data = self.get_response_data(user)

        if data:
            data.pop("access", None)
            data.pop("refresh", None)
            response = Response(
                data,
                status=status.HTTP_201_CREATED,
                headers=headers,
            )
        else:
            response = Response(status=status.HTTP_204_NO_CONTENT, headers=headers)

        return response
