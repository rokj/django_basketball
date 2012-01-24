from django.conf.urls.defaults import *
from django.views.generic.list_detail import object_detail
from django.conf import settings
from django.contrib.auth.views import login, logout
from django.views.generic.simple import redirect_to
from django.views.decorators.cache import cache_page

from common import views as common_views
from basketball import views as basketball_views

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    (r'^admin/doc/', include('django.contrib.admindocs.urls')),
    (r'^admin/', include(admin.site.urls)),
    (r'^$', post_views.main_view),

    # basketball 
    # this are examples, change it to your needs
    (r'^team/2010-2011/$', basketball_views.team_view, { 'slug': 'team-2010-2011' }),
    (r'^team/2011-2012/$', basketball_views.team_view, { 'slug': 'team-2011-2012' }),
    url(r'^game/2010-2011/$', cache_page(basketball_views.games_view, settings.CACHE_SECONDS), { 'slug': '1-league-2010-2011-west' }, name='games_view_2010-2011'),
    url(r'^game/2011-2012/$', cache_page(basketball_views.games_view, settings.CACHE_SECONDS), { 'slug': '1-league-2011-2012-west' }, name='games_view_2011-2012'),
    (r'^games/$', redirect_to, {'url': '/games/2011-2012/'}),
    url(r'^(?P<url>games/\d{4}-\d{4}/(?P<slug>[\w-]+)/(?P<date_played>\d{4}-\d{2}-\d{2}))/$', cache_page(basketball_views.game_view, settings.CACHE_SECONDS), name='game_view'),
    (r'^player/(?P<slug>[\w-]+)/$', basketball_views.player_view),
)

if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^static/(?P<path>.*)$', 'django.views.static.serve', { 'document_root': settings.MEDIA_ROOT , 'show_indexes': True }),
    )
