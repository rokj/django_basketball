# -*- coding: utf-8 -*-
from django import template
from common.functions import game_url
register = template.Library()

register.filter("game_url", game_url)
