from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from parladata.models import Law, Organization, Person


@receiver(pre_save, sender=Organization)
def copy_date_fields(sender, **kwargs):
    obj = kwargs["instance"]

    if obj.founding_date:
        obj.start_date = obj.founding_date
    if obj.dissolution_date:
        obj.end_date = obj.dissolution_date


# all instances are validated before being saved
@receiver(pre_save, sender=Person)
@receiver(pre_save, sender=Organization)
def validate_date_fields(sender, **kwargs):
    obj = kwargs["instance"]
    obj.full_clean()


@receiver(post_save, sender=Law)
def set_mdt(sender, instance, **kwargs):
    if not instance.mdt_fk and instance.mdt:
        mdt_str = instance.mdt
        mdt = Organization.objects.filter(_name__icontains=mdt_str)
        if mdt:
            instance.mdt_fk = mdt[0]
            instance.save()
