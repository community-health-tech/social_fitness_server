#!/usr/bin/env python
"""
WSGI config for storytelling_server project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/howto/deployment/wsgi/
"""

import os
import sys
from django.core.wsgi import get_wsgi_application

sys.path.append('/Users/hermansaksono/Projects/storytelling_server')

os.environ["DJANGO_SETTINGS_MODULE"] = "storytelling_server.settings"
#os.environ.setdefault("DJANGO_SETTINGS_MODULE", "storytelling_server.settings")

application = get_wsgi_application()
