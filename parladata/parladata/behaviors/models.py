import uuid
from datetime import datetime
from importlib import import_module

from autoslug import AutoSlugField
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.validators import RegexValidator
from django.db import models
from django.db.models import Q
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from taggit.managers import TaggableManager


class Parsable(models.Model):
    parser_names = models.TextField(
        verbose_name=_("parser_names"),
        help_text=_(
            "Variations of a name e.g. 'Janez Janša|Ivan Janez Janša' that the parser considers equal"
        ),
        blank=True,
        null=True,
    )

    class Meta:
        abstract = True

    def add_parser_name(self, new_parser_name):
        if not self.parser_names:
            self.parser_names = new_parser_name
        else:
            if not new_parser_name in self.parser_names_as_list:
                self.parser_names = f"{self.parser_names}|{new_parser_name}"

    @property
    def parser_names_as_list(self):
        if not self.parser_names:
            return []
        else:
            return self.parser_names.split("|")


class Timestampable(models.Model):
    """
    An abstract base class model that provides self-updating
    ``created`` and ``modified`` fields.
    """

    created_at = models.DateTimeField(
        verbose_name=_("created_at"),
        help_text=_("The time the object was created."),
        auto_now_add=True,
        db_index=True,
    )
    updated_at = models.DateTimeField(
        verbose_name=_("updated_at"),
        help_text=_("The time the object was last updated."),
        auto_now=True,
        db_index=True,
    )

    class Meta:
        abstract = True


class ValidAtQuerySet(models.QuerySet):
    def valid_at(self, timestamp):
        return self.filter(
            Q(valid_from__lte=timestamp) | Q(valid_from__isnull=True),
            Q(valid_to__gte=timestamp) | Q(valid_to__isnull=True),
        )


class Versionable(models.Model):
    """
    An abstract base class model that provides versioning fields
    ``valid_from`` and ``valid_to``
    """

    valid_from = models.DateTimeField(
        verbose_name=_("valid_from"),
        help_text=_(
            "Leave blank if the value hasn't changed. If the vales changes insert the time and the the value is valid from."
        ),
        blank=True,
        null=True,
        default=None,
    )
    valid_to = models.DateTimeField(
        verbose_name=_("valid_to"),
        help_text=_(
            "Leave blank if the value hasn't changed. If the vales changes insert the time and the the value is valid to. Then add a new entry for the value."
        ),
        blank=True,
        null=True,
        default=None,
    )

    objects = ValidAtQuerySet.as_manager()

    class Meta:
        abstract = True


# TODO touch on delete
class VersionableProperty(Versionable):
    owner = None
    value = models.TextField(
        verbose_name=_("value"),
        help_text=_("Insert approriate value"),
        blank=False,
        null=False,
    )

    class Meta:
        abstract = True

    def __str__(self):
        return str(self.value)

    # after we save a versionable property
    # we should make sure its owner updates
    # its updated_at timestamp
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.owner.touch()


class VersionableFieldsOwner(models.Model):
    @staticmethod
    def versionable_property_on_date(owner, property_model_name, timestamp):
        versionable_properties_module = import_module(
            "parladata.models.versionable_properties"
        )
        PropertyModel = getattr(versionable_properties_module, property_model_name)
        active_properties = PropertyModel.objects.valid_at(timestamp).filter(
            owner=owner
        )

        if active_properties.count() > 1:
            # TODO maybe a more descriptive exception is appropriate
            raise Exception(
                f"More than one active {property_model_name} at {timestamp}. Check your data."
            )

        return active_properties.first()

    @staticmethod
    def versionable_property_value_on_date(owner, property_model_name, datetime):
        active_property = VersionableFieldsOwner.versionable_property_on_date(
            owner, property_model_name, datetime
        )
        if active_property:
            return active_property.value
        return None

    # this was a dead end, but I'm leaving it here
    # if anyone gets any good ideas
    # TODO remove if not used in 2022
    def latest_versionable_property_timestamp_before(self, timestamp):
        versionable_properties = map(
            lambda x: x.model,
            filter(lambda x: x.attname == "owner_id", self._meta._relation_tree),
        )
        timestamps = []
        for versionable_property in versionable_properties:
            try:
                latest_versionable_property = versionable_property.objects.filter(
                    owner=self
                ).latest("valid_from")

                if latest_versionable_property.valid_from:
                    timestamps.append(latest_versionable_property.valid_from)
            except versionable_property.DoesNotExist:
                pass

        if len(timestamps) == 0:
            return datetime.now()

        # sort in place
        timestamps.sort()
        return timestamps[-1]

    # this is used by versionable properties
    # to effectively bust the cache
    def touch(self):
        self.updated_at = datetime.now()
        self.save()

    class Meta:
        abstract = True


class Taggable(models.Model):
    tags = TaggableManager(blank=True)

    class Meta:
        abstract = True


class Sluggable(models.Model):
    @property
    def slug(self):
        if self.name:
            return slugify(f"{self.id}-{self.name}")
        return str(self.id)

    class Meta:
        abstract = True


class Approvable(models.Model):
    """
    An abstract base class model that provides
    ``approved_at`` and ``rejecated_at`` fields.
    """

    approved_at = models.DateTimeField(
        verbose_name=_("approved_at"),
        help_text=_("Insert the date when the item was approved"),
        null=True,
        blank=True,
        db_index=True,
    )
    rejected_at = models.DateTimeField(
        verbose_name=_("rejected_at"),
        help_text=_("Insert the date when the item was rejected"),
        null=True,
        blank=True,
        db_index=True,
    )

    class Meta:
        abstract = True
