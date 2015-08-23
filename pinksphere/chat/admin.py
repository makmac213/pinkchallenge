from django.contrib import admin

# chat
from .models import (ChatRequest, ChatQueue, Notification, 
                        MasterAvailability, ChatMessage)


class ChatRequestAdmin(admin.ModelAdmin):
    pass


class ChatQueueAdmin(admin.ModelAdmin):
    pass


class NotificationAdmin(admin.ModelAdmin):
    pass


class MasterAvailabilityAdmin(admin.ModelAdmin):
    pass


class ChatMessageAdmin(admin.ModelAdmin):
    pass

admin.site.register(ChatRequest, ChatRequestAdmin)
admin.site.register(ChatQueue, ChatQueueAdmin)
admin.site.register(Notification, NotificationAdmin)
admin.site.register(MasterAvailability, MasterAvailabilityAdmin)
admin.site.register(ChatMessage, ChatMessageAdmin)