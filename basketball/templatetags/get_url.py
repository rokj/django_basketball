# -*- coding: utf-8 -*-
from django import template
from common.functions import get_url
register = template.Library()

# for future use
# https://docs.djangoproject.com/en/dev/howto/custom-template-tags/#assignment-tags
# register.simple_tag(takes_context=True)(get_url)
