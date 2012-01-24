# -*- coding: utf-8 -*-
from django import template
from datetime import datetime
from django.conf import settings
from common.functions import player_url
register = template.Library()

register.filter("player_url", player_url)
