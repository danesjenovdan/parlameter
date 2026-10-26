from django.contrib import admin

from parladata.models.summary import Summary


@admin.register(Summary)
class SummaryAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "title",
        "legislation",
        "approved_at",
        "created_at",
        "updated_at",
    )
    search_fields = ("text",)
    readonly_fields = ("created_at", "updated_at")
    autocomplete_fields = ("link",)

    def title(self, obj):
        return obj.text[:100] if obj.text else None

    def legislation(self, obj):
        return (
            f"{obj.link.legislation.epa}" if obj.link and obj.link.legislation else None
        )
