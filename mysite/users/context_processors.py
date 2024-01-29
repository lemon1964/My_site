from posts.utils import menu


def get_posts_context(request):
    return {'mainmenu': menu}
