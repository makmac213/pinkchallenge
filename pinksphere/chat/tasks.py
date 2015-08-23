from django.conf import settings
from django.contrib.auth.models import User, Group

# djcelery
from celery import task

# chat
from .models import ChatRequest, Notification


@task
def send_chat_notifications(request):
    # this function will be called through celery
    # and should run async
    group = settings.MEMBER_DISCIPLE
    masters = User.objects.filter(groups=group)
    for master in masters:
        notification = Notification()
        notification.master = master
        notification.chat_request = request
        notification.save()
    print "(%s) notifications sent" % (len(masters))