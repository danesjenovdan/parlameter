from django.contrib import admin


class LatestScoresAdmin(admin.ModelAdmin):
    """A ModelAdmin that displays the latest valid score."""

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        latest_score_timestamp = qs.order_by("-timestamp").first().timestamp

        return qs.filter(timestamp=latest_score_timestamp).order_by("-value")
