from parladata.models import Law, LegislationStatus, Motion


def contains_any(text, options):
    for option in options:
        if option in text:
            return True
    return False


def set_legislation_result():
    in_procedure = LegislationStatus.objects.get(name="in_procedure")
    rejected = LegislationStatus.objects.get(name="rejected")
    enacted = LegislationStatus.objects.get(name="enacted")
    final_vote_titles = ["predlog Akta", "predlog Odloka"]
    for legislation in Law.objects.filter(passed=None):
        motions = legislation.motions.all()
        for motion in motions:
            if contains_any(motion.title, final_vote_titles):
                if motion.result != None:
                    legislation.passed = motion.result
                    if motion.result:
                        legislation.status = enacted
                    else:
                        legislation.status = rejected
                    legislation.save()

        if legislation.status == None:
            legislation.status = in_procedure
            legislation.save()
