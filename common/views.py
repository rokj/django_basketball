from django.http import Http404, HttpResponseRedirect

from posts.models import Post
from basketball.models import Game
from custom_comments.models import CustomComment
from common.functions import game_url, post_url

def comment_redirect(request, type):
    if request.GET['c']:
        comment_id = request.GET['c']
        comment = CustomComment.objects.get(pk=comment_id)

        if type == "post":
            post = Post.objects.get(pk=comment.object_pk)

            if post:
                return HttpResponseRedirect(post_url(post) + "#komentar-" + str(comment.comment_number))
        elif type == "game":
            game = Game.objects.get(pk=comment.object_pk)

            if game:
                return HttpResponseRedirect(game_url(game, game.contest.season) + "#komentar-" + str(comment.comment_number))

    return HttpResponseRedirect("/")
