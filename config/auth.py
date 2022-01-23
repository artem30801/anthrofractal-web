from django.contrib.auth.middleware import PersistentRemoteUserMiddleware
from django.contrib.auth.backends import RemoteUserBackend


class AutheliaMiddleware(PersistentRemoteUserMiddleware):
    header = "HTTP_REMOTE_USER"  # consider using request.headers["Remote-User"]

    # def process_request(self, request):
    #     username = request.META.get(self.header)
    #     print("AUTH REQUEST?", self.header, username, request)
    #     super().process_request(request)


class AutheliaBackend(RemoteUserBackend):
    def configure_user(self, request, user):
        user.set_unusable_password()
        user.save()
        return super().configure_user(request, user)
