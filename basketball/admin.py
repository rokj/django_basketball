import datetime
from django.contrib import admin
from django import forms
from django.db import models
from django.forms import ModelForm
from django.forms.widgets import Select
from django.utils.translation import ugettext_lazy as _

from basketball.models import PlayerImage, Player, Personnel, Team, TeamImage, TeamPlayer, Contest, ContestTeam, Game, GameImage, GameVideo, GameStatistics, Club, ClubImage, LogoImage, GamePlayerStatistics, ContestStandings

class ContestStandingsAdmin(admin.ModelAdmin):
    list_display = ('contest', 'game_round', 'team', 'games_played', 'wins', 'losses')
    ordering = ('-wins', 'losses')

class PlayerImageAdmin(admin.ModelAdmin):
    exclude = ('created_by', 'updated_by', 'datetime_deleted')

    def save_form(self, request, form, change):
        obj = super(PlayerImageAdmin, self).save_form(request, form, change)

        if not change:
            obj.created_by = request.user
            obj.updated_by = request.user

        return obj

class GameImageAdmin(admin.ModelAdmin):
    exclude = ('created_by', 'updated_by', 'name', 'datetime_deleted')

    def save_form(self, request, form, change):
        obj = super(GameImageAdmin, self).save_form(request, form, change)

        if not change:
            obj.created_by = request.user
            obj.updated_by = request.user

        return obj

class GameVideoAdmin(admin.ModelAdmin):
    exclude = ('created_by', 'updated_by', 'datetime_deleted')

    def save_form(self, request, form, change):
        obj = super(GameVideoAdmin, self).save_form(request, form, change)

        if not change:
            obj.created_by = request.user
            obj.updated_by = request.user

        return obj

class TeamPlayerAdminForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(TeamPlayerAdminForm, self).__init__(*args, **kwargs)
        self.fields["team"].widget = Select()
        self.fields["team"].queryset = Team.objects.order_by('name')
        self.fields["player"].widget = Select()
        self.fields["player"].queryset = Player.objects.order_by('first_name', 'last_name',)

class TeamPlayerAdmin(admin.ModelAdmin):
    exclude = ('created_by', 'updated_by', 'datetime_deleted')
    ordering = ('-team', 'player__first_name', 'player__last_name')
    form = TeamPlayerAdminForm

    class Meta:
        model = TeamPlayer

    def save_form(self, request, form, change):
        obj = super(TeamPlayerAdmin, self).save_form(request, form, change)

        if not change:
            obj.created_by = request.user
            obj.updated_by = request.user

        return obj

class GamePlayerStatisticsAdminForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(GamePlayerStatisticsAdminForm, self).__init__(*args, **kwargs)
        self.fields["game"].widget = Select()
        self.fields["game"].queryset = Game.objects.order_by('-datetime_played')
        self.fields["player"].widget = Select()
        self.fields["player"].queryset = Player.objects.order_by('first_name', 'last_name',)

class GamePlayerStatisticsAdmin(admin.ModelAdmin):
    exclude = ('created_by', 'updated_by', 'datetime_deleted')
    ordering = ('-game', '-datetime_created',)
    form = GamePlayerStatisticsAdminForm

    class Meta:
        model = GamePlayerStatistics

    def save_form(self, request, form, change):
        obj = super(GamePlayerStatisticsAdmin, self).save_form(request, form, change)

        if not change:
            obj.created_by = request.user
            obj.updated_by = request.user

        return obj

class GameAdminForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(GameAdminForm, self).__init__(*args, **kwargs)
        self.fields["team1"].widget = Select()
        self.fields["team1"].queryset = Team.objects.order_by('name', 'season',)
        self.fields["team2"].widget = Select()
        self.fields["team2"].queryset = Team.objects.order_by('name', 'season',)
        self.fields["winner"].widget = Select()
        self.fields["winner"].queryset = Team.objects.order_by('name', 'season',)

        if 'instance' in kwargs:
            game_images = self.instance.images.all()
            images = self.fields['images'].widget
            choices = []
            for choice in game_images:
                choices.append((choice.id, choice.description))
            images.choices = choices

            game_videos = self.instance.videos.all()
            videos = self.fields['videos'].widget
            choices = []
            for choice in game_videos:
                choices.append((choice.id, choice.name))
            videos.choices = choices
        else:
            images = self.fields['images'].widget
            images.choices = []

            videos = self.fields['videos'].widget
            videos.choices = []

def recalc_standings(modeladmin, request, queryset):
    if request.user:
        games = Game.objects.filter(pk__in=queryset)
        contests = []
        for game in games:
            if game.contest not in contests:
                contests.append(game.contest)

        for contest in contests:
            ContestStandings.recalc_standings(contest, request.user)

recalc_standings.short_description = _(u"Recalculate standings")

class GameAdmin(admin.ModelAdmin):
    formfield_overrides = { models.TextField: {'widget': forms.Textarea(attrs={'class':'ckeditor'})}, }
    ordering = ('-datetime_played',)
    exclude = ('created_by', 'updated_by', 'datetime_deleted')
    list_per_page = 100
    search_fields = ['team1', 'team2', ]
    filter_horizontal = ('images',)
    form = GameAdminForm
    actions = [recalc_standings]

    def save_form(self, request, form, change):
        obj = super(GameAdmin, self).save_form(request, form, change)

        if not change:
            obj.created_by = request.user
            obj.updated_by = request.user

        return obj

    class Media:
        js = ('ckeditor/ckeditor.js',)
        css = {'all': ('css/admin.css',)}

    # kudos
    # http://techblog.ironfroggy.com/2011/02/django-how-to-hook-in-after-multiple.html
    def response_change(self, request, obj):
        response = super(GameAdmin, self).response_change(request, obj)

        Game.delete_non_related_images()

        return response

    def response_add(self, request, obj, *args, **kwargs):
        response = super(GameAdmin, self).response_add(request, obj, *args, **kwargs)

        Game.delete_non_related_images()

        return response

    # kudos
    # http://stackoverflow.com/questions/4343535/django-admin-make-a-field-read-only-when-modifying-obj-but-required-when-adding/4346448#4346448
    def get_readonly_fields(self, request, obj=None):
        if obj: # editing an existing object
            return self.readonly_fields + ('contest',)
        return self.readonly_fields

class ContestTeamAdmin(admin.ModelAdmin):
    exclude = ('created_by', 'updated_by', 'datetime_deleted')

    def save_form(self, request, form, change):
        obj = super(ContestTeamAdmin, self).save_form(request, form, change)

        if not change:
            obj.created_by = request.user
            obj.updated_by = request.user

        return obj

class PlayersAdmin(admin.ModelAdmin):
    exclude = ('created_by', 'updated_by', 'datetime_deleted')
    ordering = ('first_name', 'last_name',)
    prepopulated_fields = {'slug': ('first_name', 'last_name',)}

    def save_form(self, request, form, change):
        obj = super(PlayersAdmin, self).save_form(request, form, change)

        if not change:
            obj.created_by = request.user
            obj.updated_by = request.user

        return obj

class PersonnelAdmin(admin.ModelAdmin):
    exclude = ('created_by', 'updated_by', 'datetime_deleted')
    ordering = ('first_name', 'last_name',)
    prepopulated_fields = {'slug': ('first_name', 'last_name',)}

    def save_form(self, request, form, change):
        obj = super(PersonnelAdmin, self).save_form(request, form, change)

        if not change:
            obj.created_by = request.user
            obj.updated_by = request.user

        return obj

class TeamAdmin(admin.ModelAdmin):
    exclude = ('created_by', 'updated_by', 'datetime_deleted')
    ordering = ('-datetime_created',)

    def save_form(self, request, form, change):
        obj = super(TeamAdmin, self).save_form(request, form, change)

        if not change:
            obj.created_by = request.user
            obj.updated_by = request.user

        return obj

class ClubAdmin(admin.ModelAdmin):
    exclude = ('created_by', 'updated_by', 'datetime_deleted')

    class Meta:
        model = TeamPlayer

    def save_form(self, request, form, change):
        obj = super(ClubAdmin, self).save_form(request, form, change)

        if not change:
            obj.created_by = request.user
            obj.updated_by = request.user

        return obj

admin.site.register(Game, GameAdmin)
admin.site.register(GameImage, GameImageAdmin)
admin.site.register(GameVideo, GameVideoAdmin)
admin.site.register(PlayerImage, PlayerImageAdmin)
admin.site.register(Player, PlayersAdmin)
admin.site.register(Personnel, PersonnelAdmin)
admin.site.register(Team, TeamAdmin)
admin.site.register(TeamImage)
admin.site.register(TeamPlayer, TeamPlayerAdmin)
admin.site.register(Contest)
admin.site.register(ContestTeam, ContestTeamAdmin)
admin.site.register(GameStatistics)
admin.site.register(Club, ClubAdmin)
admin.site.register(ClubImage)
admin.site.register(LogoImage)
admin.site.register(GamePlayerStatistics, GamePlayerStatisticsAdmin)

admin.site.register(ContestStandings, ContestStandingsAdmin)
