from django.contrib import admin

# chat
from .models import (ChatRequest, ChatQueue, Notification, 
                        MasterAvailability)


class ChatRequestAdmin(admin.ModelAdmin):
    pass


class ChatQueueAdmin(admin.ModelAdmin):
    pass


class NotificationAdmin(admin.ModelAdmin):
    pass


class MasterAvailabilityAdmin(admin.ModelAdmin):
    pass


admin.site.register(ChatRequest, ChatRequestAdmin)
admin.site.register(ChatQueue, ChatQueueAdmin)
admin.site.register(Notification, NotificationAdmin)
admin.site.register(MasterAvailability, MasterAvailabilityAdmin)