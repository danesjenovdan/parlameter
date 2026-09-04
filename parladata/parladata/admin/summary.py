from django.contrib import admin

from parladata.models.summary import Summary


@admin.register(Summary)
class SummaryAdmin(admin.ModelAdmin):
    list_display = ("id", "text", "is_approved", "created_at", "updated_at")
    search_fields = ("text",)
    readonly_fields = ("created_at", "updated_at")
    autocomplete_fields = ("link",)
