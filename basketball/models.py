import os

from tagging.fields import TagField

from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from django.db import models
from django.db.models import Q
from django.db.models.signals import m2m_changed
from django.core.urlresolvers import reverse
from django.db.models.signals import post_save
from django.core.cache import cache
from django.http import HttpRequest
from django.utils.cache import get_cache_key
from django.db.models.signals import post_save
from django.conf import settings

from common.models import Skeleton, SkeletonU
from common.functions import get_random_string, get_image_path, game_url

PLAYING_POSITION = (
    ('C-F', 'C-F'),
    ('C-G', 'C-G'),
    ('F-G', 'F-G'),
    ('F-C', 'F-C'),
    ('G', 'G'),
    ('F', 'F'),
    ('1', '1'),
    ('2', '2'),
    ('3', '3'),
    ('4', '4'),
    ('5', '5'),
)

"""
1P = 1 point - made
2P = 2 points - made
3P = 3 points - made
1PM = 1 point - missed
2PM = 2 points - missed
3PM = 3 points - missed
A = Assist
R = Rebound
B = Block
S = Steal
F = Foul
T = Tehnical foul
"""

GAME_ACTION = (
    ('1P', '1P'),
    ('2P', '2P'),
    ('3P', '3P'),
    ('1PM', '1PM'),
    ('2PM', '2PM'),
    ('3PM', '3PM'),
    ('A', 'A'),
    ('R', 'R'),
    ('B', 'B'),
    ('S', 'S'),
    ('F', 'F'),
    ('T', 'T')
)

PLAY_STATUS = (
    ('PLAYED', 'PLAYED'),
    ('DNP', 'DNP'),
    ('INACTIVE', 'INACTIVE')
)

class PlayerImage(SkeletonU):
    name = models.CharField(_('Image name'), max_length=100, blank=False, null=False)
    description = models.CharField(_('Image description'), max_length=255, blank=True, null=True)
    image = models.ImageField(upload_to=get_image_path("img/player", "basketball_playerimage"), null=False)
    original_filename = models.CharField(_('Original filename'), max_length=255, blank=True, null=True)
    tags = TagField()

    def __unicode__(self):
        return self.name

    def save(self):
        self.original_filename = self.image.name
        super(PlayerImage, self).save()

class Player(SkeletonU):
    user = models.ForeignKey(User, related_name='(app_label)s_%(class)s_user', null=True, blank=True)
    first_name = models.CharField(_('First name'), max_length=30, null=True, blank=True)
    last_name = models.CharField(_('Last name'), max_length=30, null=False, blank=False)
    birthday = models.DateField(_('Birthday'), null=True, blank=True)
    birthday_year = models.PositiveIntegerField(_('Birth year'), null=True, blank=True)
    height = models.PositiveIntegerField(_('Height'), null=True, blank=True)
    weight = models.PositiveIntegerField(_('Weight'), null=True, blank=True)
    number = models.PositiveIntegerField(_('Number'), null=True, blank=True)
    playing_position = models.CharField(_('Playing position'), max_length=3, null=True, blank=True, choices=PLAYING_POSITION)
    info = models.TextField(_('Additional info'), null=True, blank=True)
    stat_active = models.NullBooleanField(_('Show statistics for player'), null=True, blank=True)
    slug = models.SlugField(
        _('Slug'),
        help_text=_('Player slug.'),
        null=True,
        db_index=True,
        blank=False,
        default='',
        unique=True
    )

    images = models.ManyToManyField(PlayerImage, null=True, blank=True)

    __unicode__ = lambda self: u'%s %s' % (self.first_name, self.last_name)

class PersonnelImage(SkeletonU):
    name = models.CharField(_('Image name'), max_length=100, blank=False, null=False)
    description = models.CharField(_('Image description'), max_length=255, blank=True, null=True)
    image = models.ImageField(upload_to=get_image_path("img/personnel", "basketball_personnelimage"), null=False)
    original_filename = models.CharField(_('Original filename'), max_length=255, blank=True, null=True)
    tags = TagField()

    def __unicode__(self):
        return self.name

    def save(self):
        self.original_filename = self.image.name
        super(PersonnelImage, self).save()

class Personnel(SkeletonU):
    user = models.ForeignKey(User, related_name='(app_label)s_%(class)s_user', null=True, blank=True)
    first_name = models.CharField(_('First name'), max_length=30, blank=True)
    last_name = models.CharField(_('Last name'), max_length=30, blank=True)
    birthday = models.DateTimeField(_('Birthday'), null=True, blank=True)
    birthday_year = models.PositiveIntegerField(_('Birth year'), null=True, blank=True)
    years_active = models.CharField(_('Years active'), help_text=_("Separated by comma."), max_length=100, blank=True)
    position = models.CharField(_('Position'), max_length=100, blank=True)
    info = models.TextField(_('Additional info'), null=True, blank=True)
    slug = models.SlugField(
        _('Slug'),
        help_text=_('Presonnel slug.'),
        null=False,
        db_index=True,
        blank=False,
        default='',
        unique=True
    )

    images = models.ManyToManyField(PersonnelImage, null=True, blank=True)

    __unicode__ = lambda self: u'%s %s' % (self.first_name, self.last_name)

class LogoImage(SkeletonU):
    name = models.CharField(_('Image name'), max_length=100, blank=False, null=False)
    description = models.CharField(_('Image description'), max_length=255, blank=True, null=True)
    image = models.ImageField(upload_to=get_image_path("img/logo", "basketball_logoimage"), null=False)
    original_filename = models.CharField(_('Original filename'), max_length=255, blank=True, null=True)
    tags = TagField()

    def __unicode__(self):
        return self.name

    def save(self):
        self.original_filename = self.image.name
        super(LogoImage, self).save()

class ClubImage(SkeletonU):
    name = models.CharField(_('Image name'), max_length=100, blank=False, null=False)
    description = models.CharField(_('Image description'), max_length=255, blank=True, null=True)
    image = models.ImageField(upload_to=get_image_path("img/club", "basketball_clubimage"), null=False)
    original_filename = models.CharField(_('Original filename'), max_length=255, blank=True, null=True)
    tags = TagField()

    def __unicode__(self):
        return self.name

    def save(self):
        self.original_filename = self.image.name
        super(ClubImage, self).save()

class Club(SkeletonU):
    """
    created == club creation date
    """
    name = models.CharField(_('Club name'), max_length=40, blank=False, null=False)
    description = models.CharField(_('Club description'), max_length=255, blank=True, null=True)
    created = models.DateTimeField(null=True, blank=True)
    info = models.TextField(_('Additional info'), blank=True, null=True)
    slug = models.SlugField(
        _('Slug'),
        help_text=_('Club slug.'),
        null=False,
        db_index=True,
        blank=False,
        default='',
        unique=True
    )

    images = models.ManyToManyField(ClubImage, null=True, blank=True)
    logo = models.ManyToManyField(LogoImage, null=True, blank=True)

    __unicode__ = lambda self:  u'%s' % (self.name)

class TeamImage(SkeletonU):
    name = models.CharField(_('Image name'), max_length=100, blank=False, null=False)
    description = models.CharField(_('Image description'), max_length=255, blank=True, null=True)
    image = models.ImageField(upload_to=get_image_path("img/team", "basketball_teamimage"), null=False)
    original_filename = models.CharField(_('Original filename'), max_length=255, blank=True, null=True)
    tags = TagField()

    def __unicode__(self):
        return self.name

    def save(self):
        self.original_filename = self.image.name
        super(TeamImage, self).save()

class Team(SkeletonU):
    name = models.CharField(_('Team name'), max_length=40, blank=False, null=False)
    season = models.CharField(_('Team year/season'), max_length=30, null=False, blank=False)
    info = models.TextField(_('Additional info'), blank=True, null=True)
    club = models.ForeignKey(Club, related_name='%(app_label)s_%(class)s_club', null=True, blank=True)
    slug = models.SlugField(
        _('Slug'),
        help_text=_('Team slug.'),
        null=False,
        db_index=True,
        blank=False,
        default='',
        unique=True
    )
    our_team = models.BooleanField(_('Our team?'), default=False, null=False, blank=False)

    images = models.ManyToManyField(TeamImage, null=True, blank=True)

    __unicode__ = lambda self:  u'%s (%s)' % (self.name, self.season)

class TeamPlayer(SkeletonU):
    team = models.ForeignKey(Team, related_name='%(app_label)s_%(class)s_team')
    player = models.ForeignKey(Player, related_name='%(app_label)s_%(class)s_player')

    __unicode__ = lambda self: u'%s -- %s' % (self.team, self.player)

class Contest(SkeletonU):
    """
    Contest model class.

    contest_type == contest type e.g. tournament, league
    """
    name = models.CharField(_('Contest name'), max_length=40, null=False, blank=False)
    contest_type = models.CharField(_('Contest type'), max_length=20, null=True, blank=True)
    season = models.CharField(_('Contest year/season'), max_length=30, null=False, blank=False)
    info = models.TextField(_('Additional info'), blank=True, null=True)
    slug = models.SlugField(
        _('Slug'),
        help_text=_('Contest slug.'),
        null=False,
        db_index=True,
        blank=False,
        default='',
        unique=True
    )

    __unicode__ = lambda self: u'%s -- %s' % (self.name, self.season)

class ContestTeam(SkeletonU):
    contest = models.ForeignKey(Contest, related_name='%(app_label)s_%(class)s_contest')
    team = models.ForeignKey(Team, related_name='%(app_label)s_%(class)s_team')

    __unicode__ = lambda self: u'%s -- %s' % (self.contest, self.team)

class GameImage(SkeletonU):
    name = models.CharField(_('Image name'), max_length=100, blank=True, null=True)
    description = models.CharField(_('Image description'), max_length=255, blank=True, null=True)
    image = models.ImageField(upload_to=get_image_path("img/game", "basketball_gameimage"), null=False)
    original_filename = models.CharField(_('Original filename'), max_length=255, blank=True, null=True)
    tags = TagField()

    __unicode__ = lambda self: u'%s. %s' % (self.pk, self.description)

    def save(self):
        self.original_filename = self.image.name
        super(GameImage, self).save()

class GameVideo(SkeletonU):
    name = models.CharField(_('Video name'), max_length=100, blank=False, null=False)
    description = models.CharField(_('Video description'), max_length=255, blank=True, null=True)
    url = models.URLField(_('URL of a video'), max_length=255, blank=True, null=True, verify_exists=False)
    screenshot = models.CharField(_('Video screenshot'), max_length=255, blank=True, null=True)
    video = models.FileField(upload_to=get_image_path("videos/upload", "basketball_gamevideo"), null=True, blank=True)
    original_filename = models.CharField(_('Original filename'), max_length=255, blank=True, null=True)
    tags = TagField()

    __unicode__ = lambda self: u'%s' % (self.name)

    def save(self):
        self.original_filename = self.video.name
        super(GameVideo, self).save()

class Game(SkeletonU):
    """
    URL to get game:
    
    {{ SITE_URL }}/games/1996-1997/<contest>/<slug>/<date>/
    {{ SITE_URL }}/games/1996-1997/nba/chicago-bulls-vs-utah-jazz/1996-10-23/
    """
    contest = models.ForeignKey(Contest, related_name='%(app_label)s_%(class)s_contest', null=False, blank=False)
    game_round = models.PositiveIntegerField(_('Game round in season'), null=False, blank=False)
    datetime_played = models.DateTimeField(_('Datetime played'), null=False, blank=False)
    datetime_published = models.DateTimeField(_('Datetime published'), null=True, blank=True)
    team1 = models.ForeignKey(Team, related_name='%(app_label)s_%(class)s_team1', null=False, blank=False)
    team2 = models.ForeignKey(Team, related_name='%(app_label)s_%(class)s_team2', null=False, blank=False)
    winner = models.ForeignKey(Team, related_name='%(app_label)s_%(class)s_winner', null=True, blank=True)
    score_q1_t1 = models.PositiveIntegerField(_('Score of the first team in first quarter'), null=True, blank=True)
    score_q1_t2 = models.PositiveIntegerField(_('Score of the second team in first quarter'), null=True, blank=True)
    score_q2_t1 = models.PositiveIntegerField(_('Score of the first team in second quarter'), null=True, blank=True)
    score_q2_t2 = models.PositiveIntegerField(_('Score of the second team in second quarter'), null=True, blank=True)
    score_q3_t1 = models.PositiveIntegerField(_('Score of the first team in third quarter'), null=True, blank=True)
    score_q3_t2 = models.PositiveIntegerField(_('Score of the second team in third quarter'), null=True, blank=True)
    score_q4_t1 = models.PositiveIntegerField(_('Score of the first team in fourth quarter'), null=True, blank=True)
    score_q4_t2 = models.PositiveIntegerField(_('Score of the second team in fourth quarter'), null=True, blank=True)
    score1 = models.PositiveIntegerField(_('Score of the first team'), null=False, blank=False)
    score2 = models.PositiveIntegerField(_('Score of the second team'), null=False, blank=False)
    title = models.CharField(_('Game title'), null=True, blank=True, max_length=50)
    excerpt = models.TextField(_('Game excerpt'), null=True, blank=True)
    info = models.TextField(_('Game info'), null=True, blank=True)
    featured = models.BooleanField(_('Featured'), help_text=_('Do we show it on front page for example?'), blank=True, default=False)
    published = models.BooleanField(_('Game published'), blank=True, default=False)
    tags = TagField()
    location = models.CharField(_('Location'), help_text=_('Location where game has been played'), max_length=255, null=True, blank=True)
    hall_arena = models.CharField(_('Hall/arena name'), help_text=_('In some countries instead of location, hall name is being provided for location'), max_length=255, null=True, blank=True)
    attendance = models.PositiveIntegerField(_('attendance'), null=True, blank=True)
    judges = models.CharField(_('Judges'), max_length=255, blank=True, null=True)
    commissioners = models.CharField(_('Commissioners'), max_length=255, blank=True, null=True)

    slug = models.SlugField(
        _('Slug'),
        help_text=_('Game slug.'),
        null=False,
        db_index=True,
        blank=False,
        default='',
        unique=False
    )

    images = models.ManyToManyField(GameImage, null=True, blank=True)
    videos = models.ManyToManyField(GameVideo, null=True, blank=True)

    class Meta:
        unique_together = ('slug', 'datetime_played',)

    __unicode__ = lambda self: u'%s - %s. krog %s vs %s' % (self.contest, self.game_round, self.team1, self.team2)

    def save(self, *args, **kwargs):
        updating = self.pk
        model = super(Game, self).save(*args, **kwargs)
        if self.team1 and self.team2 and self.published == True:
            if not updating:
                ContestStandings.recalc_game(self, self.created_by)
            else:
                ContestStandings.recalc_standings(self.contest, self.updated_by)

    @staticmethod
    def delete_non_related_images():
        related_images = []
        for game in Game.objects.all():
            for image in game.images.all():
                related_images.append(image.pk)

        if related_images and len(related_images) > 0:
            not_related_images = GameImage.objects.exclude(pk__in=related_images)
        else:
            not_related_images = GameImage.objects.exclude()

        if not_related_images and len(not_related_images) > 0:
            for nr_image in not_related_images:
                if os.path.exists(nr_image.image.path):
                    os.remove(nr_image.image.path)

        if not_related_images and len(not_related_images) > 0:
            GameImage.objects.filter(pk__in=[nr_images.pk for nr_images in not_related_images]).delete()

class GameStatistics(SkeletonU):
    game = models.ForeignKey(Game, related_name='%(app_label)s_%(class)s_game')
    what = models.CharField(_('What happened'), max_length=2, null=False, blank=False, choices=GAME_ACTION)
    when = models.CharField(_('Time occured'), max_length=20, null=True, blank=True)
    who_player = models.ForeignKey(Player, related_name='%(app_label)s_%(class)s_who_player', null=True, blank=True)
    who_personnel = models.ForeignKey(Personnel, related_name='%(app_label)s_%(class)s_who_personnel', null=True, blank=True)

class GamePlayerStatistics(SkeletonU):
    game = models.ForeignKey(Game, related_name='%(app_label)s_%(class)s_game', null=False, blank=False)
    player = models.ForeignKey(Player, related_name='%(app_label)s_%(class)s_player', null=False, blank=False)
    min = models.CharField(_('Minutes played'), max_length=5, null=True, blank=True)
    fgm_m = models.PositiveIntegerField(_('Field goals made'), null=True, blank=True)
    fgm_a = models.PositiveIntegerField(_('Field goals attempts'), null=True, blank=True)
    pm3_m = models.PositiveIntegerField(_('3 points made'), null=True, blank=True)
    pm3_a = models.PositiveIntegerField(_('3 points attempts'), null=True, blank=True)
    ftm_m = models.PositiveIntegerField(_('Free throw made'), null=True, blank=True)
    ftm_a = models.PositiveIntegerField(_('Free throw attempts'), null=True, blank=True)
    reb_d = models.PositiveIntegerField(_('Defensive rebounds'), null=True, blank=True)
    reb_o = models.PositiveIntegerField(_('Offensive rebounds'), null=True, blank=True)
    ast = models.PositiveIntegerField(_('Offensive rebounds'), null=True, blank=True)
    pf = models.PositiveIntegerField(_('Personal fouls'), null=True, blank=True)
    st = models.PositiveIntegerField(_('Steals'), null=True, blank=True)
    to = models.PositiveIntegerField(_('Turnovers'), null=True, blank=True)
    bs = models.PositiveIntegerField(_('Blocks'), null=True, blank=True)
    ba = models.PositiveIntegerField(_('Blocks against'), null=True, blank=True)
    pts = models.PositiveIntegerField(_('Points'), null=True, blank=True)
    play_status = models.CharField(_('Play status'), max_length=10, null=True, blank=True, choices=PLAY_STATUS)

    __unicode__ = lambda self: u'%s - %s (PTS: %s)' % (self.game, self.player, self.pts)

class ContestStandings(SkeletonU):
    contest = models.ForeignKey(Contest, related_name='%(app_label)s_%(class)s_contest1', null=False, blank=False)
    game_round = models.PositiveIntegerField(_('Game round in season'), null=False, blank=False)
    team = models.ForeignKey(Team, null=False, blank=False)
    standing = models.PositiveIntegerField(_('Position in contest'), null=True, blank=True)
    games_played = models.PositiveIntegerField(_('Games played'), null=True, blank=True)
    wins = models.PositiveIntegerField(_('Wins'), null=True, blank=True)
    losses = models.PositiveIntegerField(_('Losses'), null=True, blank=True)
    points_given = models.PositiveIntegerField(_('Points given'), null=True, blank=True)
    points_received = models.PositiveIntegerField(_('Points received'), null=True, blank=True)
    points_diff = models.IntegerField(_('Difference in points given/received'), null=True, blank=True)
    standing_points = models.IntegerField(_('Standing points'), null=True, blank=True)

    __unicode__ = lambda self: u'%s: %s. %s' % (self.contest, self.game_round, self.team)

    @staticmethod
    def recalc_game_team(game, team, user):
        try:
            standing = ContestStandings.objects.get(contest=game.contest, game_round=game.game_round, team=team)
            standing.updated_by = user
        except ContestStandings.DoesNotExist:
            standing = ContestStandings(contest=game.contest, game_round=game.game_round, team=team, created_by=user)
            standing.save()

        games_played = Game.objects.filter(Q(game_round__lte=game.game_round), Q(contest=game.contest, team1=team) | Q(contest=game.contest, team2=team)).count()
        wins = Game.objects.filter(contest=game.contest, winner=team, game_round__lte=game.game_round).count()
        points_given = 0
        points_received = 0

        games = Game.objects.filter(contest=game.contest, team1=team, game_round__lte=game.game_round)
        for g in games:
            points_given += g.score1
            points_received += g.score2
        games = Game.objects.filter(contest=game.contest, team2=team, game_round__lte=game.game_round)
        for g in games:
            points_given += g.score2
            points_received += g.score1

        standing.games_played = games_played
        standing.wins = wins
        standing.losses = standing.games_played - standing.wins
        standing.points_given = points_given
        standing.points_received = points_received
        standing.points_diff = standing.points_given - standing.points_received
        # TODO: standing.standing_points
        standing.save()

    @staticmethod
    def recalc_game(game, user):
        ContestStandings.recalc_game_team(game, game.team1, user)
        ContestStandings.recalc_game_team(game, game.team2, user)

    @staticmethod
    def recalc_standings(contest, user):
        ContestStandings.objects.filter(contest=contest).delete()

        games = Game.objects.filter(contest=contest)
        for game in games:
            ContestStandings.recalc_game(game, user)

# kudos
# http://stackoverflow.com/questions/1995126/invalidating-a-path-from-the-django-cache-recursively
def expire_page(path):
    request = HttpRequest()
    request.path = path
    request.method = 'GET'
    key = get_cache_key(request)
    if cache.has_key(key):
        cache.delete(key)

def invalidate_cache(sender, **kwargs):
    if kwargs['instance'].contest.season == '2010-2011':
        expire_page(reverse("games_view_2010-2011", args=[]))
    elif kwargs['instance'].contest.season == '2011-2012':
        expire_page(reverse("games_view_2011-2012", args=[]))

    expire_page(game_url(kwargs['instance'], kwargs['instance'].contest.season).replace(settings.SITE_URL, ""))

post_save.connect(invalidate_cache, sender=Game)
