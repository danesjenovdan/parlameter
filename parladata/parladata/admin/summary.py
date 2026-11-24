from django.contrib import admin

from parladata.models.summary import Summary


@admin.register(Summary)
class SummaryAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "title",
        "law",
        "approved_at",
        "created_at",
        "updated_at",
    )
    search_fields = ("text",)
    readonly_fields = ("created_at", "updated_at")
    autocomplete_fields = ("links",)

    def title(self, obj):
        return obj.text[:100] if obj.text else None
