# -*- coding: utf-8 -*-
from django import template
from datetime import datetime
from django.conf import settings
from common.functions import replace
register = template.Library()

register.filter("replace", replace)
