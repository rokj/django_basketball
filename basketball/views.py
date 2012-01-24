from random import randint
from datetime import datetime, timedelta
from decimal import Decimal
from sets import Set
import math, re, os, subprocess

from django.http import Http404
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.db.models import Q, Avg, Sum
from django.conf import settings

from common.models import Settings
from common.functions import get_url, contains
from basketball.models import Team, Player, TeamPlayer, Contest, ContestTeam, Game, GameImage, GamePlayerStatistics, ContestStandings
from curses import has_key

def contest_order(item):
    return (-item.wins, item.losses)

def team_view(request, slug):
    __args = {}
    team = Team.objects.filter(slug=slug)

    if team:
        team_players = TeamPlayer.objects.filter(team=team[0]).order_by('player__first_name', 'player__last_name')
        __args["team"] = team
        __args["team_players"] = team_players

    __args["current_url"] = get_url(request)
    __args["SITE_URL"] = settings.SITE_URL

    # maybe would you like to set this to something like
    #  __args["title"] = "Team 2011-2012"

    return render_to_response('basketball/team.html', __args, context_instance=RequestContext(request))

def games_view(request, slug):
    __args = {}

    contest_standings = {}
    js_standings = {}
    round_games = {}

    contest = Contest.objects.get(slug=slug)

    our_games = []
    __contest_standings = {}
    __contest_teams = ContestTeam.objects.filter(contest=contest)
    contest_teams = [cs.team.pk for cs in __contest_teams]
    our_team = Team.objects.get(pk__in=contest_teams, our_team=True)
    games = Game.objects.filter(Q(team1=our_team) | Q(team2=our_team), contest=contest, published=True).order_by('-game_round')
    __round_games = Game.objects.filter(~Q(team1=our_team) & ~Q(team2=our_team), contest=contest, published=True).order_by('-game_round')
    for rg in __round_games:
        if not rg.game_round in round_games:
            round_games[rg.game_round] = []
        round_games[rg.game_round].append(rg)

    if games:
        for game in games:
            __game = {}
            __game["game"] = game

            __top_player = {}

            team1_players = TeamPlayer.objects.filter(team=game.team1)
            team2_players = TeamPlayer.objects.filter(team=game.team2)

            top_pts1 = GamePlayerStatistics.objects.filter(game=game, player__in=[tp.player.id for tp in team1_players]).order_by("-pts")
            if top_pts1:
                __game["top_pts1"] = { "player": top_pts1[0].player, "pts": top_pts1[0].pts }

            top_pts2 = GamePlayerStatistics.objects.filter(game=game, player__in=[tp.player.id for tp in team2_players]).order_by("-pts")
            if top_pts2:
                __game["top_pts2"] = { "player": top_pts2[0].player, "pts": top_pts2[0].pts }

            our_games.append(__game)

    game_rounds = 0
    teams = []

    contest_standings = ContestStandings.objects.filter(contest=contest).order_by('-game_round')

    if (contest_standings):
        game_rounds = contest_standings[0].game_round

    for cs in contest_standings:
        if cs.team not in teams:
            teams.append(cs.team)

    standings = {}

    if contest_standings and game_rounds > 0:
        i = 1
        while i <= game_rounds:
            round = []
            round_teams = []
            missing_teams = []
            for cs in contest_standings:
                if cs.game_round == i:
                    round.append(cs)
                    round_teams.append(cs.team)

            if len(round_teams) < teams and i > 1:
                missing_teams = filter(lambda x: x not in round_teams, teams)

            if len(missing_teams) > 0:
                for mt in missing_teams:
                    previous_round = i - 1
                    while previous_round >= 1:
                        for cs in contest_standings:
                            if cs.team == mt and cs.game_round == previous_round:
                                round.append(cs)
                                previous_round = 1
                                break
                        previous_round -= 1

            standings[i] = round
            i += 1

        for __round, __teams in standings.iteritems():
            __teams.sort(key=contest_order)

        """
        json example
        
        for __round, __teams in contests[contest.pk]["standings"].iteritems():
            js_standings[__round] = [{"team_id": t.team.pk, "team_name": t.team.name, "games_played": t.games_played, "wins": t.wins, "losses": t.losses, "points_given": t.points_given, "points_received": t.points_received, "points_diff": t.points_diff} for t in __teams]

        js_standings = simplejson.dumps(js_standings, indent=2, ensure_ascii=False)
        contests[contest.pk]["js_standings"] = js_standings
        """

    __args["standings"] = standings
    if len(round_games) > 0:
        __args["round_games"] = round_games
    __args["our_games"] = our_games
    __args["contest"] = contest
    __args["title"] = "Tekme " + contest.name + " v sezoni " + contest.season
    __args["current_url"] = get_url(request)
    __args["SITE_URL"] = settings.SITE_URL

    return render_to_response('basketball/games.html', __args, context_instance=RequestContext(request))

def game_view(request, url, slug, date_played):
    date_played = datetime.strptime(date_played, '%Y-%m-%d')
    dp_tomorrow = date_played + timedelta(days=1)

    __args = {}
    game = Game.objects.filter(slug=slug, datetime_played__gt=date_played, datetime_played__lt=dp_tomorrow)

    if game and len(game) > 0:
        __args["game"] = game[0]

        __team1_players = TeamPlayer.objects.filter(team=game[0].team1)
        __team2_players = TeamPlayer.objects.filter(team=game[0].team2)

        team1_players = []
        for tp in __team1_players:
            team1_players.append(tp.player_id)

        team2_players = []
        for tp in __team2_players:
            team2_players.append(tp.player_id)

        players_stats_team1 = GamePlayerStatistics.objects.filter(game=game[0], player__in=team1_players).order_by("-pts")
        players_stats_team2 = GamePlayerStatistics.objects.filter(game=game[0], player__in=team2_players).order_by("-pts")

        __args["team_stats_1"] = {}
        __args["team_stats_1"]["ft_avg"] = None
        __args["team_stats_1"]["ft_a"] = None
        __args["team_stats_1"]["ft_m"] = None
        __args["team_stats_1"]["pm3_m_avg"] = None
        __args["team_stats_1"]["pm3_a_avg"] = None
        __args["team_stats_1"]["pm3s"] = None

        __args["team_stats_2"] = {}
        __args["team_stats_2"]["ft_avg"] = None
        __args["team_stats_2"]["ft_a"] = None
        __args["team_stats_2"]["ft_m"] = None
        __args["team_stats_2"]["pm3_m_avg"] = None
        __args["team_stats_2"]["pm3_a_avg"] = None
        __args["team_stats_2"]["pm3s"] = None

        __args["team_stats_1"]["pts_avg"] = players_stats_team1.aggregate(Avg('pts'))["pts__avg"]
        __args["team_stats_1"]["pts_sum"] = players_stats_team1.aggregate(Sum('pts'))["pts__sum"]
        __args["team_stats_1"]["pm3_m_avg"] = players_stats_team1.aggregate(Avg('pm3_m'))
        __args["team_stats_1"]["pm3s"] = players_stats_team1.aggregate(Sum('pm3_m'))["pm3_m__sum"]

        ftm_a = players_stats_team1.aggregate(Sum('ftm_a'))
        ftm_m = players_stats_team1.aggregate(Sum('ftm_m'))
        if ftm_a["ftm_a__sum"] is not None and ftm_m["ftm_m__sum"] is not None:
            __args["team_stats_1"]["ft_a"] = Decimal(ftm_a["ftm_a__sum"])
            __args["team_stats_1"]["ft_m"] = Decimal(ftm_m["ftm_m__sum"])
            __args["team_stats_1"]["ft_avg"] = Decimal(ftm_m["ftm_m__sum"]) / Decimal(ftm_a["ftm_a__sum"])
            __args["team_stats_1"]["ft_avg_percent"] = int(math.fmod(round(Decimal(ftm_m["ftm_m__sum"]) / Decimal(ftm_a["ftm_a__sum"]), 2), 100) * 100)

        __args["team_stats_2"]["pts_avg"] = players_stats_team2.aggregate(Avg('pts'))["pts__avg"]
        __args["team_stats_2"]["pts_sum"] = players_stats_team2.aggregate(Sum('pts'))["pts__sum"]
        __args["team_stats_2"]["pm3_m_avg"] = players_stats_team2.aggregate(Avg('pm3_m'))
        __args["team_stats_2"]["pm3s"] = players_stats_team2.aggregate(Sum('pm3_m'))["pm3_m__sum"]

        ftm_a = players_stats_team2.aggregate(Sum('ftm_a'))
        ftm_m = players_stats_team2.aggregate(Sum('ftm_m'))
        if ftm_a["ftm_a__sum"] is not None and ftm_m["ftm_m__sum"] is not None:
            __args["team_stats_2"]["ft_a"] = Decimal(ftm_a["ftm_a__sum"])
            __args["team_stats_2"]["ft_m"] = Decimal(ftm_m["ftm_m__sum"])
            __args["team_stats_2"]["ft_avg"] = Decimal(ftm_m["ftm_m__sum"]) / Decimal(ftm_a["ftm_a__sum"])
            __args["team_stats_2"]["ft_avg_percent"] = int(math.fmod(round(Decimal(ftm_m["ftm_m__sum"]) / Decimal(ftm_a["ftm_a__sum"]), 2), 100) * 100)

        contest_standings = ContestStandings.objects.filter(contest=game[0].contest).order_by('-game_round')

        rround = []
        teams = []
        round_teams = []
        missing_teams = []

        for cs in contest_standings:
            if cs.team not in teams:
                teams.append(cs.team)

        for cs in contest_standings:
            if cs.game_round == game[0].game_round:
                rround.append(cs)
                round_teams.append(cs.team)

        if len(round_teams) < teams and game[0].game_round > 1:
            missing_teams = filter(lambda x: x not in round_teams, teams)

        if len(missing_teams) > 0:
            for mt in missing_teams:
                previous_round = game[0].game_round - 1
                while previous_round >= 1:
                    for cs in contest_standings:
                        if cs.team == mt and cs.game_round == previous_round:
                            rround.append(cs)
                            previous_round = 1
                            break
                    previous_round -= 1

        if rround and len(rround) > 0:
            rround.sort(key=contest_order)
            __args["round_standings"] = rround

        __args["players_stats_team1"] = players_stats_team1
        __args["players_stats_team2"] = players_stats_team2
        __args["contest"] = __args["game"].contest
        current_contest_season = Settings.objects.get(key="contests_in_player_stats")
        __args["current_contest_season"] = current_contest_season.value
        __args["title"] = __args["game"].team1.name + " " + str(__args["game"].score1) + " : " + str(__args["game"].score2) + " " + __args["game"].team2.name

    # temporary, since now we have only one video to show. In case of multiple videos
    # we will have to change this
    if "game" in __args and __args["game"] and len(__args["game"].videos.all()) > 0:
        video_on_fs = re.sub(settings.MEDIA_URL, settings.MEDIA_ROOT, __args["game"].videos.all()[0].url)
        if not re.search("http", video_on_fs):
            try:
                __args["game_video_size"] = os.path.getsize(video_on_fs)
                __args["game_video_size"] = "%0.1f MB" % (__args["game_video_size"] / (1024 * 1024.0))

                output = subprocess.Popen(['ffmpeg', '-i', video_on_fs], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                for line in output.stdout.readlines():
                    aspect = re.findall(r'DAR (\d+:\d+)', line)
                    if len(aspect) > 0:
                        if aspect[0] == "4:3":
                            __args["game_video_width"] = 560
                            __args["game_video_height"] = 420

                            break
                        elif aspect[0] == "16:9":
                            __args["game_video_width"] = 521
                            __args["game_video_height"] = 294

                            break

                    if not "game_video_width" in __args and not "game_video_height" in __args:
                        dimensions = re.findall(r' (\d+x\d+) ', line)
                        if len(dimensions) > 0:
                            if dimensions[0] == "720x576":
                                __args["game_video_width"] = 560
                                __args["game_video_height"] = 420

                                break
                            elif dimensions[0] == "524x420":
                                __args["game_video_width"] = 521
                                __args["game_video_height"] = 294

                                break

            except OSError:
                __args["game_video_size"] = ""

    __args["current_url"] = get_url(request)
    __args["SITE_URL"] = settings.SITE_URL

    return render_to_response('basketball/game.html', __args, context_instance=RequestContext(request))

def player_view(request, slug):
    __args = {}

    player = Player.objects.filter(slug=slug)
    if player and len(player) > 0:
        __args["player"] = player[0]
        __args["game_player_stats"] = {}
        __args["game_player_stats"]["contest_stats_js"] = {}
        __args["game_player_stats"]["career_stats_js"] = ""
        __args["contests"] = None

        game_player_stats = GamePlayerStatistics.objects.filter(player=player[0])
        if game_player_stats and len(game_player_stats) > 0:
            if not "career_stats" in __args["game_player_stats"]:
                __args["game_player_stats"]["career_stats"] = {}

            __args["game_player_stats"]["career_stats"]["pts_avg"] = game_player_stats.aggregate(Avg('pts'))
            __args["game_player_stats"]["career_stats"]["pm3_m_avg"] = game_player_stats.aggregate(Avg('pm3_m'))
            ftm_a = game_player_stats.aggregate(Sum('ftm_a'))
            ftm_m = game_player_stats.aggregate(Sum('ftm_m'))
            if ftm_a["ftm_a__sum"] is not None and ftm_m["ftm_m__sum"] is not None:
                __args["game_player_stats"]["career_stats"]["ft_avg"] = int(math.fmod(round(Decimal(ftm_m["ftm_m__sum"]) / Decimal(ftm_a["ftm_a__sum"]), 2), 100) * 100)
                __args["game_player_stats"]["career_stats"]["ftm_a__sum"] = ftm_a["ftm_a__sum"]
                __args["game_player_stats"]["career_stats"]["ftm_m__sum"] = ftm_m["ftm_m__sum"]

            # we try to find all contests in which player played
            game_contests = Game.objects.filter(id__in=[ps.game.id for ps in game_player_stats]).values('contest').distinct()
            if game_contests and len(game_contests) > 0:
                # now we only show those, we like (from settings)
                gc_ids = [gc["contest"] for gc in game_contests]
                try:
                    contests_in_player_stats = Settings.objects.get(key="contests_in_player_stats")
                    gc_ids = contests_in_player_stats.value.split(",")
                except Settings.DoesNotExist:
                    pass

                contests = Contest.objects.filter(id__in=gc_ids)
                if contests and len(contests) > 0:
                    __args["contests"] = contests

            # let us get statistics for player per contest
            career_game_player_stats = []
            if "contests" in __args and __args["contests"] is not None:
                for c in __args["contests"]:
                    contest_games = Game.objects.filter(contest=c).order_by("datetime_played")
                    if contest_games and len(contest_games) > 0:
                        __played_in = Set(cg.id for cg in contest_games) & Set(ps.game.id for ps in game_player_stats)
                        __played_in = Game.objects.filter(id__in=list(__played_in)).order_by("datetime_played")
                        played_in = [pi.id for pi in __played_in]
                        __contest_game_player_stats = GamePlayerStatistics.objects.filter(player=player[0], game__in=played_in)
                        contest_game_player_stats = []
                        i = 0
                        while i < len(__played_in):
                            for cgps in __contest_game_player_stats:
                                if cgps.game.id == played_in[0]:
                                    contest_game_player_stats.append(cgps)
                                    del played_in[0]
                                    break
                            i += 1

                        for gps in game_player_stats:
                            career_game_player_stats.append(gps)
                        if contest_game_player_stats and len(contest_game_player_stats) > 0:
                            if not "contest_stats" in __args["game_player_stats"]:
                                __args["game_player_stats"]["contest_stats"] = {}

                            if not "pts_avg" in __args["game_player_stats"]:
                                __args["game_player_stats"]["pts_avg"] = {}

                            if not "pm3_m_avg" in __args["game_player_stats"]:
                                __args["game_player_stats"]["pm3_m_avg"] = {}

                            if not "pm3s" in __args["game_player_stats"]:
                                __args["game_player_stats"]["pm3s"] = {}

                            if not "ft_avg" in __args["game_player_stats"]:
                                __args["game_player_stats"]["ft_avg"] = {}

                            if not "ft_avg_percent" in __args["game_player_stats"]:
                                __args["game_player_stats"]["ft_avg_percent"] = {}

                            if not "ft_a" in __args["game_player_stats"]:
                                __args["game_player_stats"]["ft_a"] = {}

                            if not "ft_m" in __args["game_player_stats"]:
                                __args["game_player_stats"]["ft_m"] = {}

                            __args["game_player_stats"]["contest_stats"][c.slug] = contest_game_player_stats
                            __args["game_player_stats"]["pts_avg"][c.slug] = __contest_game_player_stats.aggregate(Avg('pts'))["pts__avg"]
                            __args["game_player_stats"]["pm3_m_avg"][c.slug] = __contest_game_player_stats.aggregate(Avg('pm3_m'))
                            __args["game_player_stats"]["pm3s"][c.slug] = __contest_game_player_stats.aggregate(Sum('pm3_m'))

                            ftm_a = __contest_game_player_stats.aggregate(Sum('ftm_a'))
                            ftm_m = __contest_game_player_stats.aggregate(Sum('ftm_m'))
                            if ftm_a["ftm_a__sum"] is not None and ftm_m["ftm_m__sum"] is not None:
                                __args["game_player_stats"]["ft_a"][c.slug] = Decimal(ftm_a["ftm_a__sum"])
                                __args["game_player_stats"]["ft_m"][c.slug] = Decimal(ftm_m["ftm_m__sum"])
                                __args["game_player_stats"]["ft_avg"][c.slug] = Decimal(ftm_m["ftm_m__sum"]) / Decimal(ftm_a["ftm_a__sum"])
                                __args["game_player_stats"]["ft_avg_percent"][c.slug] = int(math.fmod(round(Decimal(ftm_m["ftm_m__sum"]) / Decimal(ftm_a["ftm_a__sum"]), 2), 100) * 100)

                            __args["game_player_stats"]["contest_stats_js"][c.slug] = ','.join(["[\"" + cgps.game.datetime_played.strftime("%Y-%m-%d") + "\", " + str(cgps.pts) + "]" for cgps in contest_game_player_stats])

            if "contest_stats_js" in __args["game_player_stats"] and len(__args["game_player_stats"]["contest_stats_js"]) > 0:
                __args["game_player_stats"]["career_stats_js"] = ','.join([contest_stats_js for contest, contest_stats_js in __args["game_player_stats"]["contest_stats_js"].iteritems()])

        __args["title"] = player[0].first_name + " " + player[0].last_name

    __args["current_url"] = get_url(request)
    __args["SITE_URL"] = settings.SITE_URL

    return render_to_response('basketball/player.html', __args, context_instance=RequestContext(request))
