from datetime import datetime

from django import forms
from django.conf import settings
from django.contrib import admin
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.safestring import mark_safe

from parlacards.admin.filters import MembersListFilter
from parlacards.models import GroupTfidf, PersonTfidf, Quote, SessionTfidf
from parladata.admin.filters import (
    MembersAndLeaderListFilter,
    MembersListFilter,
    OrganizationsListFilter,
    SessionListFilter,
)
from parladata.models.memberships import PersonMembership


class SessionTfidfAdmin(admin.ModelAdmin):
    list_display = ("session_name", "token", "value", "created_at", "delete")
    list_filter = (SessionListFilter,)
    search_fields = ["session__name"]
    list_per_page = 20
    ordering = ["-timestamp", "-value"]
    list_editable = ("token",)
    autocomplete_fields = ["session"]
    deleted_session_fk = None

    def get_queryset(self, request):
        return SessionTfidf.objects.all().prefetch_related("session")

    def session_name(self, obj):
        return obj.session.name

    def get_changelist_formset(self, request, **kwargs):
        data = super().get_changelist_formset(request, **kwargs)
        data.form.base_fields["token"].widget.attrs["rows"] = 1
        data.form.base_fields["token"].widget.attrs["cols"] = 25
        data.form.base_fields["token"].widget.attrs.pop("class")
        return data

    def delete(self, obj):
        return mark_safe(
            f'<input onclick="location.href=\'{obj.pk}/delete/\'" type="button" value="Delete" />'
        )

    def delete_view(self, request, object_id, extra_context=None):
        self.deleted_session_fk = SessionTfidf.objects.get(id=object_id).session_id
        return super().delete_view(request, object_id, extra_context)

    def response_delete(self, request, obj_display, obj_id):
        partial_url = reverse("admin:parlacards_sessiontfidf_changelist")
        url = f"{settings.BASE_URL}{partial_url}?session__id__exact={self.deleted_session_fk}"
        return redirect(url)

    delete.allow_tags = True
    delete.short_description = "Delete object"


class PersonTfidfAdmin(admin.ModelAdmin):
    list_display = ("person", "token", "value", "created_at", "delete")
    list_filter = (MembersAndLeaderListFilter, MembersListFilter)
    list_per_page = 20
    ordering = ["-timestamp", "-value"]
    list_editable = ("token",)
    autocomplete_fields = ["person"]
    deleted_member_fk = None

    def get_changelist_formset(self, request, **kwargs):
        data = super().get_changelist_formset(request, **kwargs)
        data.form.base_fields["token"].widget.attrs["rows"] = 1
        data.form.base_fields["token"].widget.attrs["cols"] = 25
        data.form.base_fields["token"].widget.attrs.pop("class")
        return data

    def delete(self, obj):
        return mark_safe(
            f'<input onclick="location.href=\'{obj.pk}/delete/\'" type="button" value="Delete" />'
        )

    def delete_view(self, request, object_id, extra_context=None):
        self.deleted_member_fk = PersonTfidf.objects.get(id=object_id).person_id
        return super().delete_view(request, object_id, extra_context)

    def response_delete(self, request, obj_display, obj_id):
        partial_url = reverse("admin:parlacards_persontfidf_changelist")
        url = f"{settings.BASE_URL}{partial_url}?member={self.deleted_member_fk}"
        return redirect(url)

    delete.allow_tags = True
    delete.short_description = "Delete object"


class GroupTfidfAdmin(admin.ModelAdmin):
    list_display = ("group", "token", "value", "created_at", "delete")
    list_filter = (OrganizationsListFilter, MembersListFilter)
    list_per_page = 20
    ordering = ["-timestamp", "-value"]
    list_editable = ("token",)
    autocomplete_fields = ["group"]
    deleted_group_fk = None

    def get_changelist_formset(self, request, **kwargs):
        data = super().get_changelist_formset(request, **kwargs)
        data.form.base_fields["token"].widget.attrs["rows"] = 1
        data.form.base_fields["token"].widget.attrs["cols"] = 25
        data.form.base_fields["token"].widget.attrs.pop("class")
        return data

    def delete(self, obj):
        return mark_safe(
            f'<input onclick="location.href=\'{obj.pk}/delete/\'" type="button" value="Delete" />'
        )

    def delete_view(self, request, object_id, extra_context=None):
        self.deleted_group_fk = GroupTfidf.objects.get(id=object_id).group_id
        return super().delete_view(request, object_id, extra_context)

    def response_delete(self, request, obj_display, obj_id):
        partial_url = reverse("admin:parlacards_grouptfidf_changelist")
        url = f"{settings.BASE_URL}{partial_url}?organization={self.deleted_group_fk}"
        return redirect(url)

    delete.allow_tags = True
    delete.short_description = "Delete object"


admin.site.register(SessionTfidf, SessionTfidfAdmin)
admin.site.register(PersonTfidf, PersonTfidfAdmin)
admin.site.register(GroupTfidf, GroupTfidfAdmin)
admin.site.register(Quote)
