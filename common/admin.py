import datetime
from django.contrib import admin
from django import forms
from django.db import models

from common.models import Settings

admin.site.register(Settings)
