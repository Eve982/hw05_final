import datetime


def year(request):
    return {
        'year': datetime.datetime.today().year,
    }
