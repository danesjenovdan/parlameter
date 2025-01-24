from datetime import datetime, timedelta

import tablib
from django.core.cache import cache
from django.db.models.query import QuerySet
from import_export.fields import Field
from import_export.resources import ModelResource

from parladata.models import Mandate, Organization, Person


def get_cached_person_name(id):
    cache_key = f"person_name_{id}"
    name = cache.get(cache_key)
    if not name:
        person = Person.objects.get(id=id)
        name = person.name
        cache.set(cache_key, name, 60 * 60 * 24)
    return name


def get_cached_group_name(id):
    cache_key = f"group_name_{id}"
    name = cache.get(cache_key)
    if not name:
        organization = Organization.objects.get(id=id)
        name = organization.name
        cache.set(cache_key, name, 60 * 60 * 24)
    return name


class ExportModelResource(ModelResource):
    """
    Extends ModelResource class with additional functions that allow exporting data from admin using a generator.
    """

    def get_queryset(self, mandate_id, request_id=None):
        """
        Queryset for ModelResource to work with.
        Meant to be overwritten to include filtering by mandate_id.
        """
        return self._meta.model.objects.all()

    def export_as_generator_csv(
        self, queryset=None, mandate_id=None, request_id=None, *args, **kwargs
    ):
        """
        Generator function that returns queryset in csv format.
        """
        self.before_export(queryset, *args, **kwargs)
        if queryset is None:
            queryset = self.get_queryset(mandate_id=mandate_id, request_id=request_id)
        print(queryset.count())
        headers = self.get_export_headers()
        data = tablib.Dataset(headers=headers)
        # write headers
        yield data.csv

        if isinstance(queryset, QuerySet):
            # Iterate without the queryset cache, to avoid wasting memory when
            # exporting large datasets.
            iterable = queryset.iterator()
        else:
            iterable = queryset
        for obj in iterable:
            # Return subset of the data (one row)
            data = tablib.Dataset()
            data.append(self.export_resource(obj))
            yield data.csv

        self.after_export(queryset, data, *args, **kwargs)

        yield "\n"

    def export_as_generator_json(
        self, queryset=None, mandate_id=None, request_id=None, *args, **kwargs
    ):
        """
        Generator function that returns queryset in json format.
        """
        self.before_export(queryset, *args, **kwargs)
        if queryset is None:
            queryset = self.get_queryset(mandate_id=mandate_id, request_id=request_id)

        if len(queryset) == 0:
            yield "[]"
            return

        headers = self.get_export_headers()

        # no need to yield headers because this is json
        # but we do yield start of list
        yield "["

        if isinstance(queryset, QuerySet):
            # Iterate without the queryset cache, to avoid wasting memory when
            # exporting large datasets.
            iterable = queryset.iterator()
        else:
            iterable = queryset
        for index, obj in enumerate(iterable):
            # Return subset of the data (one row)
            # here Dataset needs headers to create json keys
            data = tablib.Dataset(headers=headers)
            data.append(self.export_resource(obj))
            # data.json will return a LIST of object(s) for each iteration
            # so we cut out first '[' and last ']' and add comma
            if index != 0:
                yield ","
            yield data.json[1:-1]
            # note to self: should probably think of something less hacky

        self.after_export(queryset, data, *args, **kwargs)

        # close list at the end
        yield "]"


class CardExport(ExportModelResource):
    def get_queryset(self, mandate_id=None, request_id=None):
        """
        Queryset for CardExport to work with.
        Meant to be overwritten to include filtering by mandate_id.
        """
        if mandate_id:
            try:
                mandate = Mandate.objects.get(id=mandate_id)
                from_timestamp, to_timestamp = mandate.get_time_range_from_mandate(
                    datetime.now()
                )
                root_organization, playing_field = mandate.query_root_organizations(
                    to_timestamp - timedelta(minutes=1)
                )
                return self._meta.model.objects.filter(playing_field=playing_field)
            # if mandate does not exist return empty queryset
            except:
                return self._meta.model.objects.none()
        else:
            return self._meta.model.objects.all()
