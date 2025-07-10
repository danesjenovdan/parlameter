from django.contrib import admin

from parlanotifications.models import Keyword, NotificationUser, KeywordForAll

# Register your models here.


class UserAdmin(admin.ModelAdmin):
    list_display = ("email", "uuid")


admin.site.register(Keyword)
admin.site.register(KeywordForAll)
admin.site.register(NotificationUser, UserAdmin)
