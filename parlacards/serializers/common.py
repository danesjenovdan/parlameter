import math

from importlib import import_module

from django.core.cache import cache
from django.db.models import Avg, Max, Q

from rest_framework import serializers

from parladata.models.person import Person
from parladata.models.organization import Organization
from parladata.models.common import Mandate
from parladata.models.memberships import PersonMembership, OrganizationMembership

from parlacards.utils import truncate_score

from parladata.exceptions import NoMembershipException

from rest_framework.exceptions import NotFound

from datetime import datetime

class VersionableSerializerField(serializers.Field):
    def __init__(self, property_model_name, **kwargs):
        self.property_model_name = property_model_name
        kwargs['source'] = '*'
        kwargs['read_only'] = True
        super().__init__(**kwargs)

    def to_representation(self, value):
        if 'request_date' not in self.context.keys():
            raise Exception(f'You need to provide a date in the serializer context.')

        object_to_serialize = value
        return object_to_serialize.versionable_property_value_on_date(
            owner=object_to_serialize,
            property_model_name=self.property_model_name,
            datetime=self.context['request_date'],
        )


class ScoreSerializerField(serializers.Field):
    def __init__(self, property_model_name, **kwargs):
        self.property_model_name = property_model_name
        kwargs['source'] = '*'
        kwargs['read_only'] = True
        super().__init__(**kwargs)

    def calculate_cache_key(self, property_model_name, value_id, timestamp):
        # something like NumberOfSpokenWords_12_2021-11-13-21
        # value_id is the id of the person or organization this score belongs to
        return f'{property_model_name}_{value_id}_{timestamp.strftime("%Y-%m-%dT%H")}'

    def to_representation(self, value):
        # value is going to be the person or
        # organization we're serializing the score for
        # here we set the score_type to use later
        if isinstance(value, Person):
            score_type = 'person'
        elif isinstance(value, Organization):
            score_type = 'group'
        else:
            raise Exception(f'You should supply a person or an organization. Instead you supplied {value}.')

        if 'request_date' not in self.context.keys():
            raise Exception(f'You need to provide a date in the serializer context.')

        # TODO move score serializers to separate file or use fully qualified name
        # get the score model
        scores_module = import_module('parlacards.models')
        ScoreModel = getattr(scores_module, self.property_model_name)

        # get most recent score from this person or organization
        # that is older than the date in the context
        score_object_kwargs = {
            'timestamp__lte': self.context['request_date'],
            score_type: value,
        }
        score_object = ScoreModel.objects.filter(
            **score_object_kwargs,
        ).order_by(
            '-timestamp'
        ).first()

        # if nothing was found return error
        if not score_object:
            return {
                'error': 'No score matches your criteria.'
            }

        # check for cache
        cache_key = self.calculate_cache_key(self.property_model_name, value.id, score_object.timestamp)
        cached_content = cache.get(cache_key)

        if cached_content:
            return cached_content

        score = score_object.value

        # get ids of all the people or organizations who are
        # currently in the same playing field (organization
        # which we're calculating values for)
        if score_type == 'person':
            competition_ids = score_object.playing_field.query_voters(self.context['request_date']).values_list('id', flat=True)
        else:
            # score_type == 'organization'
            competition_ids = score_object.playing_field.query_parliamentary_groups(self.context['request_date']).values_list('id', flat=True)

        # iterate through the IDs and get their "latest" score ids
        relevant_scores_querysets = []
        for competitor_id in competition_ids:
            score_queryset_kwargs = {
                'timestamp__lte': self.context['request_date'],
                f'{score_type}__id': competitor_id
            }

            score_queryset = ScoreModel.objects.filter(
                **score_queryset_kwargs
            ).order_by(
                '-timestamp'
            )[:1]

            relevant_scores_querysets.append(score_queryset)

        relevant_score_ids = ScoreModel.objects.none().union(
            *relevant_scores_querysets
        ).values(
            'id'
        )

        relevant_scores = ScoreModel.objects.filter(id__in=relevant_score_ids)

        # aggregate max and avg
        aggregations = relevant_scores.aggregate(
            Avg('value'),
            Max('value'),
        )

        average_score = aggregations['value__avg']
        maximum_score = aggregations['value__max']

        # find out who the people or organizations with maximum scores are
        winner_ids = relevant_scores.filter(
            value__gte=truncate_score(maximum_score)
        ).values_list(f'{score_type}__id', flat=True)

        if score_type == 'person':
            maximum_competitors = Person.objects.filter(id__in=winner_ids)[:8] # max 8 fit inside the bar in card
            winners_serializer = CommonPersonSerializer(
                maximum_competitors,
                many=True,
                context=self.context
            )
        else:
            # score_type == 'organization'
            maximum_competitors = Organization.objects.filter(id__in=winner_ids)[:8] # max 8 fit inside the bar in card
            winners_serializer = CommonOrganizationSerializer(
                maximum_competitors,
                many=True,
                context=self.context
            )

        maximum_dict_key = 'members' if score_type == 'person' else 'groups'

        output = {
            'score': score,
            'average': average_score,
            'maximum': {
                'score': maximum_score,
                maximum_dict_key: winners_serializer.data
            }
        }

        cache.set(cache_key, output)
        return output


class CommonSerializer(serializers.Serializer):
    def get_fields(self, *args, **kwargs):
        fields = super().get_fields(*args, **kwargs)
        for field in fields:
            fields[field].read_only = True
        return fields


class CommonCachableSerializer(CommonSerializer):
    def calculate_cache_key(self, instance):
        raise NotImplementedError('''
            You need to define your own function to calculate the cache key.
            Maybe something like:
            `return f'ModelName_{instance.id}_{instance.updated_at.strftime("%Y-%m-%dT%H:%M:%S")}'`
        ''')

    def to_representation(self, instance):
        cache_key = self.calculate_cache_key(instance)

        # only try cache if not explicitly disabled
        if not self.context.get('GET', {}).get('no_cache', False):
            if cached_representation := cache.get(cache_key):
                return cached_representation

        representation = super().to_representation(instance)
        cache.set(cache_key, representation)
        return representation


class MandateSerializer(CommonSerializer):
    id = serializers.IntegerField()
    description = serializers.CharField()
    beginning = serializers.DateTimeField()


class CardSerializer(serializers.Serializer):
    '''
    This is a generic card serializer.

    It is to be used when you want to serialize a card
    with results. You need to implement get_results on
    the inheriting class.
    '''
    # created_at = serializers.DateTimeField()
    # updated_at = serializers.DateTimeField()

    def get_results(self, obj):
        raise NotImplementedError('You need to extend this serializer to return the results.')

    def get_mandate(self, obj):
        raise NotImplementedError('You need to extend this serializer to return the mandate.')

    results = serializers.SerializerMethodField()
    mandate = serializers.SerializerMethodField()
    # TODO
    # make the mandate dynamic
    # mandate = MandateSerializer()


class PersonScoreCardSerializer(CardSerializer):
    def __init__(self, person, *args, **kwargs):
        super().__init__(person, *args, **kwargs)
        """
        Get playing field and mandate for person
        """
        try:
            self.playing_field, self.mandate = person.get_last_playing_field_with_mandate(
                self.context['request_date']
            )
        except NoMembershipException as e:
            raise NotFound(detail=str(e), code=404)

        self.from_timestamp, self.to_timestamp = self.mandate.get_time_range_from_mandate(
            self.context['request_date']
        )
        if self.to_timestamp > self.context['request_date']:
            self.context['date'] = self.to_timestamp

    def get_person(self, obj):
        serializer = CommonPersonSerializer(obj, context=self.context)
        return serializer.data

    def get_mandate(self, obj):
        serializer = MandateSerializer(
            self.mandate,
            context=self.context
        )

        return serializer.data

    person = serializers.SerializerMethodField()


class GroupScoreCardSerializer(CardSerializer):
    def __init__(self, group, *args, **kwargs):
        super().__init__(group, *args, **kwargs)
        """
        Get playing field and mandate for group
        """
        try:
            self.playing_field, self.mandate = group.get_last_playing_field_with_mandate(
                self.context['request_date']
            )
        except NoMembershipException as e:
            raise NotFound(detail=str(e), code=404)

        self.from_timestamp, self.to_timestamp = self.mandate.get_time_range_from_mandate(
            self.context['request_date']
        )
        if self.to_timestamp > self.context['request_date']:
            self.context['date'] = self.to_timestamp

    def get_group(self, obj):
        serializer = CommonOrganizationSerializer(obj, context=self.context)
        return serializer.data

    def get_mandate(self, obj):
        serializer = MandateSerializer(
            self.mandate,
            context=self.context
        )
        return serializer.data

    group = serializers.SerializerMethodField()


class SessionScoreCardSerializer(CardSerializer):
    def get_session(self, obj):
        serializer = CommonSessionSerializer(obj, context=self.context)
        return serializer.data

    def get_mandate(self, obj):
        serializer = MandateSerializer(
            obj.mandate,
            context=self.context
        )
        return serializer.data

    session = serializers.SerializerMethodField()


class CommonPersonSerializer(CommonCachableSerializer):
    def calculate_cache_key(self, person):
        organization = person.parliamentary_group_on_date(self.context['request_date'])

        if organization:
            timestamp = max([person.updated_at, organization.updated_at])
        else:
            timestamp = person.updated_at

        return f'CommonPersonSerializer_{person.id}_{self.context["request_date"].strftime("%Y-%m-%dT%H:%M:%S")}_{timestamp.strftime("%Y-%m-%dT%H:%M:%S")}'

    def get_group(self, obj):
        active_parliamentary_group_membership = obj.parliamentary_group_on_date(self.context['request_date'])
        if not active_parliamentary_group_membership:
            return None

        serializer = CommonOrganizationSerializer(
            active_parliamentary_group_membership,
            context=self.context
        )
        return serializer.data

    def get_slug(self, person):
        memberships_count = PersonMembership.objects.filter(
            Q(member=person),
            Q(start_time__lte=self.context['request_date']) | Q(start_time__isnull=True),
            Q(end_time__gte=self.context['request_date']) | Q(end_time__isnull=True),
            Q(role__in=['voter', 'leader']),
        ).count()

        if memberships_count != 0:
            return person.slug

        return None

    slug = serializers.SerializerMethodField()
    name = VersionableSerializerField(property_model_name='PersonName')
    honorific_prefix = VersionableSerializerField(property_model_name='PersonHonorificPrefix')
    honorific_suffix = VersionableSerializerField(property_model_name='PersonHonorificSuffix')
    preferred_pronoun = VersionableSerializerField(property_model_name='PersonPreferredPronoun')
    group = serializers.SerializerMethodField()
    image = serializers.ImageField()


class CommonOrganizationSerializer(CommonCachableSerializer):
    def calculate_cache_key(self, instance):
        return f'CommonOrganizationSerializer_{instance.id}_{instance.updated_at.strftime("%Y-%m-%dT%H:%M:%S")}'

    def get_is_in_coalition(self, obj):
        return OrganizationMembership.valid_at(self.context['request_date']).filter(
            member=obj,
            organization__classification='coalition'
        ).exists()

    name = VersionableSerializerField(property_model_name='OrganizationName')
    acronym = VersionableSerializerField(property_model_name='OrganizationAcronym')
    slug = serializers.CharField()
    color = serializers.CharField()
    classification = serializers.CharField()
    is_in_coalition = serializers.SerializerMethodField()


class CommonSessionSerializer(CommonCachableSerializer):
    def calculate_cache_key(self, instance):
        # instance is session
        session_timestamp = instance.updated_at
        organization_timestamps = instance.organizations.all().values_list('updated_at', flat=True)
        timestamp = max([session_timestamp] + list(organization_timestamps))
        return f'CommonSessionSerializer_{instance.id}_{timestamp.strftime("%Y-%m-%dT%H:%M:%S")}'

    name = serializers.CharField()
    id = serializers.IntegerField()
    start_time = serializers.DateTimeField()
    end_time = serializers.DateTimeField()
    organizations = CommonOrganizationSerializer(many=True)
    classification = serializers.CharField() # TODO regular, irregular, urgent
    in_review = serializers.BooleanField()


class MonthlyAttendanceSerializer(serializers.Serializer):
    present = serializers.FloatField(source='value')
    no_mandate = serializers.FloatField()
    no_data = serializers.FloatField()
    timestamp = serializers.SerializerMethodField()

    def get_timestamp(self, obj):
        return obj.timestamp.date().isoformat()
