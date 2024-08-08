from django.conf import settings
from django.http import HttpResponse, FileResponse
from django.shortcuts import render
from django.views.decorators.clickjacking import xframe_options_sameorigin

from games.models import Game


@xframe_options_sameorigin
def game(request, game_url):

    try:
        game_object: Game = Game.objects.get(url=game_url)

        assert game_object.has_access(request.user)

        index_path = f"/games/files/{game_url}/index.html"

        return render(request, 'games/index.html', {'game': index_path, 'game_name': game_object.title})

    except Game.DoesNotExist:
        return HttpResponse("Такой игры нет", status=404)
    except AssertionError:
        return HttpResponse("У вас нет прав на эту игру", status=403)
    except Exception as e:
        return HttpResponse("Произошла ошибка", status=500)


def game_file(request, game_url, file_url):
    try:
        game_object: Game = Game.objects.get(url=game_url)

        assert game_object.has_access(request.user)

        return FileResponse(open(f"{settings.MEDIA_ROOT}/games/{game_url}/{file_url}", "rb"))

    except Game.DoesNotExist:
        return HttpResponse("Такой игры нет", status=404)
    except AssertionError:
        return HttpResponse("У вас нет прав на эту игру", status=403)
    except Exception as e:
        if request.user.is_superuser:
            return HttpResponse(f"Произошла ошибка {e}", status=500)
        else:
            return HttpResponse(f"Произошла ошибка", status=500)

