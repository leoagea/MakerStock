from .base import *  # noqa: F403

DEBUG = True
ALLOWED_HOSTS = ["*"]

# django_extensions gives us `runserver_plus`, used to serve HTTPS locally
# (self-signed, via Werkzeug) so OAuth/API callbacks that require a secure
# context work in dev. Dev-only: never added in prod.py.
INSTALLED_APPS = INSTALLED_APPS + ["django_extensions"]  # noqa: F405
