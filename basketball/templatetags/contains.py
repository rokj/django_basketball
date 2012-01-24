# -*- coding: utf-8 -*-
from django import template
from common.functions import contains
register = template.Library()

register.filter("contains", contains)
