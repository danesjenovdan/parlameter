from django.db.models import Q

from parladata.models import Law, LegislationStatus, Motion

ENACTED = LegislationStatus.objects.get(name='enacted')
ACCEPTED =  LegislationStatus.objects.get(name='submitted')
REJECTED = LegislationStatus.objects.get(name='rejected')


def set_legislation_result():
    for legislation in Law.objects.exclude(status__in=LegislationStatus.objects.filter(name__in=['rejected', 'enacted'])):
        end_motion = legislation.motions.filter(
            Q(title__icontains='v celoti') |
            Q(title__icontains='ponovno odlo') |
            Q(title__icontains='sklep mdt') |
            Q(title__icontains='sklep o primernosti predloga zakona')
        ).first()
        print('legislation')
        if end_motion:
            print('has end motion')
            set_single_legislation_result(legislation)


def is_accepeted(motion):
    accepted_option = False if 'ni primeren' in motion.text else True
    return motion.result == accepted_option

def set_single_legislation_result(legislation):
    if legislation.text:
        final_vote = Motion.objects.filter(law=legislation,
                                           title__icontains='v celoti')
        repeated_vote = Motion.objects.filter(law=legislation,
                                              title__icontains='ponovno odlo')
        mdt_vote = Motion.objects.filter(law=legislation,
                                         title__icontains='sklep mdt')
        beginning_vote = Motion.objects.filter(law=legislation,
                                               title__icontains='sklep o primernosti predloga zakona')

        print('legislation has text')
        if final_vote:
            if is_accepeted(final_vote[0]):
                ## ENACTED
                legislation.status = ENACTED
                legislation.passed = True
            else:
                ## REJECTED
                legislation.status = REJECTED
                legislation.passed = False
            legislation.save()
            return 'finished'

        elif mdt_vote:
            if is_accepeted(mdt_vote[0]):
                ## REJECTED
                legislation.status = REJECTED
                legislation.passed = False
                legislation.save()
                return 'mdt'
            else:
                ## FURTHER VOTING WILL HAPPEN
                pass


        elif beginning_vote:
            if not is_accepeted(beginning_vote[0]):
                ## REJECTED
                legislation.status = REJECTED
                legislation.passed = False
                legislation.save()
                return 'beginning'
            else:
                ## FURTHER VOTING WILL HAPPEN
                pass
    return None
