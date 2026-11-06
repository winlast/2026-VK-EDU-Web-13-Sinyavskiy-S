from . import data


def sidebar(request):
    """Блоки правой колонки, нужны на всех страницах."""
    return {
        'popular_tags': data.get_popular_tags(),
        'best_members': data.get_best_members(),
    }
