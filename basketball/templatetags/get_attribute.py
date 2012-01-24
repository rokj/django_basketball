# -*- coding: utf-8 -*-
from django import template
from datetime import datetime
from django.conf import settings
from common.functions import get_attribute
register = template.Library()

register.filter("get_attribute", get_attribute)
