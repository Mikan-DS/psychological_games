from django.http import HttpResponse, Http404
from django.shortcuts import render
from django.views.decorators.clickjacking import xframe_options_sameorigin

from games.models import Game, GameFile


@xframe_options_sameorigin
def game(request, game_url):

    try:
        game: Game = Game.objects.get(url=game_url)

        index = GameFile.objects.get(game=game, is_index=True)

        return render(request, 'games/index.html', {'game': index.file.url})
    except GameFile.DoesNotExist:
        return HttpResponse("Такой игры нет", status=404)
    except Game.DoesNotExist:
        return HttpResponse("Такой игры нет", status=404)
    except Exception as e:
        return HttpResponse("Произошла ошибка", status=500)