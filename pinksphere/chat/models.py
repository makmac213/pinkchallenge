import os
from django.db import models
from django.contrib.auth.models import User


class ChatRequest(models.Model):
    STATUS_PENDING = 1
    STATUS_ACCEPTED = 2
    STATUS_EXPIRED = 3
    STATUS_ENDED = 4
    STATUS_CHOICES = (
            (STATUS_PENDING, 'Pending'),
            (STATUS_ACCEPTED, 'Accepted'),
        )


    user = models.ForeignKey(User, related_name='chat_requests')
    accepted_by = models.ForeignKey(User, null=True, blank=True)
    status = models.IntegerField(choices=STATUS_CHOICES,
                                    default=STATUS_PENDING)
    status_date = models.DateTimeField(auto_now=True, null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    request_code = models.CharField(max_length=32)

    class Meta:
        db_table = 'chat_chat_requests'

    def __unicode__(self):
        return 'User: %s Code: %s' % (self.user.username, self.request_code)

    def generate_request_code(self):
        code = os.urandom(8).encode('hex')
        if ChatRequest.objects.filter(request_code=code).count():
            code = os.urandom(8).encode('hex')
        self.request_code = code
        return code


class ChatQueue(models.Model):
    chat_request = models.ForeignKey(ChatRequest)

    class Meta:
        db_table = 'chat_chat_queue'
        ordering = ['-chat_request__created']

    def __unicode__(self):
        return 'User: %s Code: %s' % (self.chat_request.user.username,
                                        self.chat_request.request_code)


class Notification(models.Model):
    STATUS_PENDING = 1
    STATUS_SENT = 2
    STATUS_EXPIRED = 3
    STATUS_CHOICES = (
            (STATUS_PENDING, 'Pending'),
            (STATUS_SENT, 'Sent'),
            (STATUS_EXPIRED, 'Expired'),
        )

    master = models.ForeignKey(User)
    chat_request = models.ForeignKey(ChatRequest)
    created = models.DateTimeField(auto_now_add=True)
    status = models.IntegerField(choices=STATUS_CHOICES, 
                                    default=STATUS_PENDING)

    class Meta:
        db_table = 'chat_notifications'

    def __unicode__(self):
        return 'Code: %s Master: %s' % (self.chat_request.request_code,
                                            self.master.username)


class MasterAvailability(models.Model):
    """
    When a master user has logged-in create a record.
    When master user relogged-in check for previous record
    then delete and create a new one
    """
    STATUS_AVAILABLE = 1
    STATUS_ENGAGED = 2
    STATUS_ON_BREAK = 3
    STATUS_CHOICES = (
            (STATUS_AVAILABLE, 'Available'),
            (STATUS_ENGAGED, 'Engaged'),
            (STATUS_ON_BREAK, 'On break'),        
        )

    user = models.ForeignKey(User)
    status = models.IntegerField(choices=STATUS_CHOICES, 
                                    default=STATUS_AVAILABLE)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'chat_master_availabilities'
        verbose_name_plural = 'available masters'

    def __unicode__(self):
        return 'User: %s Status: %s' % (self.user.username, 
                                            self.get_status_display())