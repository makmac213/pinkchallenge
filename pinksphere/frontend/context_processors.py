from django.conf import settings

def user_infos(request):
    context = {
        'USER_GROUP': 0,
        'MEMBER_MASTER': settings.MEMBER_MASTER,
        'MEMBER_DISCIPLE': settings.MEMBER_DISCIPLE,
    }
    if request.user.is_authenticated():
        # master and disciple
        if request.user.groups.filter(id=settings.MEMBER_MASTER).count():
            context['USER_GROUP'] = settings.MEMBER_MASTER
        elif request.user.groups.filter(id=settings.MEMBER_DISCIPLE).count():
            context['USER_GROUP'] = settings.MEMBER_DISCIPLE
    return context