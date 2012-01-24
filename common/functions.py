# -*- coding: utf-8 -*-
import string, os, re
from random import choice
from django.db import connection, transaction
from django.conf import settings
from django.core.mail import EmailMultiAlternatives

def get_random_string(length=8, chars=string.letters + string.digits):
    return ''.join([choice(chars) for i in xrange(length)])

def get_url(context):
    return context.META["HTTP_HOST"] + context.META["PATH_INFO"]

DEFAULT_IMAGE_PATH = "images/omg"
def get_image_path(path, table_name):
    """
    DEFAULT_IMAGE_PATH should happen once in a life time. You better know why.
    """
    def upload_callback(instance, filename):
        if not filename or len(filename) == 0:
            filename = instance.image.name
        cursor = connection.cursor()

        ext = os.path.splitext(filename)[1]
        ext = ext.lower()

        random_filename = get_random_string(length=8)
        tries = 0
        while tries < 3:
            cursor.execute('SELECT * FROM ' + table_name + ' WHERE image = %s', [random_filename])
            row = cursor.fetchone()
            if row:
                tries += 1
                random_filename = get_random_string(length=8)
            else:
                break

        if tries == 3:
            return DEFAULT_IMAGE_PATH

        # instance.original_filename = filename
        return '%s/%s' % (path, random_filename + ext)

    return upload_callback

# Taken from django_hitcount.
# This is not intended to be an all-knowing IP address regex.
IP_RE = re.compile('\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}')

def get_ip(request):
    """
    Retrieves the remote IP address from the request data.  If the user is
    behind a proxy, they may have a comma-separated list of IP addresses, so
    we need to account for that.  In such a case, only the first IP in the
    list will be retrieved.  Also, some hosts that use a proxy will put the
    REMOTE_ADDR into HTTP_X_FORWARDED_FOR.  This will handle pulling back the
    IP from the proper place.

    **NOTE** This function was taken from django-tracking (MIT LICENSE)
             http://code.google.com/p/django-tracking/
    """

    # if neither header contain a value, just use local loopback
    ip_address = request.META.get('HTTP_X_FORWARDED_FOR',
                                  request.META.get('REMOTE_ADDR', '127.0.0.1'))
    if ip_address:
        # make sure we have one and only one IP
        try:
            ip_address = IP_RE.match(ip_address)
            if ip_address:
                ip_address = ip_address.group(0)
            else:
                # no IP, probably from some dirty proxy or other device
                # throw in some bogus IP
                ip_address = '10.0.0.1'
        except IndexError:
            pass

    return ip_address

def post_url(post):
    if post.category:
        return settings.SITE_URL + "/" + post.category.slug + "/" + post.slug + "/"
    else:
        return settings.SITE_URL + "/" + post.slug + "/"

def game_url(game, season):
    return settings.SITE_URL + "/games/" + season + "/" + game.slug + "/" + game.datetime_played.strftime("%Y-%m-%d") + "/"

def player_url(player):
    return settings.SITE_URL + "/player/" + player.slug + "/"

def replace(string, args):
    search = args.split(args[0])[1]
    replace = args.split(args[0])[2]

    return re.sub(search, replace, string)

def get_attribute(value, arg):
    numeric_test = re.compile("^\d+$")

    """Gets an attribute of an object dynamically from a string name"""
    if hasattr(value, str(arg)):
        return getattr(value, arg)
    elif hasattr(value, 'has_key') and value.has_key(arg):
        return value[arg]
    elif numeric_test.match(str(arg)) and len(value) > int(arg):
        return value[int(arg)]
    else:
        return ""

def contains(value, arg):
    expression = re.compile(arg)
    if expression.search(value):
        return True

    return False

def send_mass_email(sender, to=None, bcc=None, subject=None, txt=None, html=None, attachment=None):
    """
    This is commmon email send function for KK Velike Lašče.
    We always send in html and txt form.
    
    sender example: 'Sender name <sender@internet.net>'
    receiver: ['email-1@email.net', ['email-2@email.net', ...]
    """

    message = EmailMultiAlternatives(subject, txt, sender, to, bcc, headers={'Reply-To': sender})
    message.attach_alternative(html, "text/html")
    message.content_subtype = "html"
    message.send()
