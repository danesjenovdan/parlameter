from django.core.paginator import Paginator
from django.utils.functional import cached_property

from parlacards.solr import get_speeches_from_solr, get_votes_from_solr, get_legislation_from_solr, get_agenda_items_from_solr


def valid_positive_int(number, default):
    try:
        if isinstance(number, float) and not number.is_integer():
            raise ValueError
        number = int(number)
    except (TypeError, ValueError):
        number = default
    if number < 1:
        number = default
    return number


def parse_pagination_query_params(params, prefix=''):
    requested_page = valid_positive_int(params.get(f'{prefix}page', None), 1)
    requested_per_page = valid_positive_int(params.get(f'{prefix}per_page', None), 10)

    return (requested_page, requested_per_page)


def pagination_response_data(paginator, page, prefix=''):
    return {
        f'{prefix}count': paginator.count,
        f'{prefix}pages': paginator.num_pages,
        f'{prefix}page': page.number,
        f'{prefix}per_page': paginator.per_page
    }


def create_paginator(params, object_list, prefix=''):
    requested_page, requested_per_page = parse_pagination_query_params(params, prefix)
    paginator = Paginator(object_list, requested_per_page)
    page = paginator.get_page(requested_page)
    metadata = pagination_response_data(paginator, page, prefix)
    return page.object_list, metadata


def create_solr_paginator(params, solr_params, prefix='', document_type='speech'):
    requested_page, requested_per_page = parse_pagination_query_params(params, prefix)
    paginator = SolrPaginator(solr_params, requested_per_page, document_type=document_type)
    page = paginator.get_page(requested_page)
    metadata = pagination_response_data(paginator, page, prefix)
    return page.object_list, metadata


class SolrPaginator(Paginator):
    def __init__(self, solr_params, per_page, orphans=0,
                 allow_empty_first_page=True, document_type='speech'):
        super().__init__(
            object_list=None,
            per_page=per_page,
            orphans=orphans,
            allow_empty_first_page=allow_empty_first_page,
        )

        self.solr_params = solr_params
        self.document_type = document_type
        self.search_method = None

        if self.document_type == 'vote':
            self.search_method = get_votes_from_solr
        elif self.document_type == 'law':
            self.search_method = get_legislation_from_solr
        elif self.document_type == 'agenda_item':
            self.search_method = get_agenda_items_from_solr
        else:
            self.search_method = get_speeches_from_solr

    @cached_property
    def count(self):
        """Return the total number of objects, across all pages."""
        _, count = self.search_method(**self.solr_params, page=1, per_page=0)
        return count

    def page(self, number):
        """Return a Page object for the given 1-based page number."""
        number = self.validate_number(number)
        bottom = (number - 1) * self.per_page
        top = bottom + self.per_page
        if top + self.orphans >= self.count:
            top = self.count

        # I'm not sure why this is called bottom and top, but Paginator slices
        # object_list like this `object_list[bottom:top]`
        objects, _ = self.search_method(**self.solr_params, page=number, per_page=self.per_page)
        return self._get_page(objects, number, self)


# TODO document how this works and make sure the assertion holds
def calculate_cache_key_for_page(object_list, metadata):
    meta_sorted_items = sorted(metadata.items())
    meta_string_items = map(lambda tuple: f'{tuple[0]}={tuple[1]}', meta_sorted_items)
    meta_string = '_'.join(meta_string_items)

    # if object_list is an empty queryset call to max() fails
    assert object_list.count() > 0

    latest_timestamp = max(map(lambda item: item.updated_at, object_list))
    return f'{meta_string}_{latest_timestamp.strftime("%Y-%m-%dT%H:%M:%S")}'
