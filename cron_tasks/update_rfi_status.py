import datetime
from apps.vendors.models import Rfis, RfiParticipationStatus


def update_rfi_status():
    print("Started update_rfi_status at {}".format(str(datetime.datetime.now())))

    try:
        current_date = datetime.datetime.today()
        opened_rfies = Rfis.objects.filter(active=True, open_datetime__date__lt=current_date,
                                           issue_datetime__date__gt=current_date).exclude(rfi_status="Opened")
        issued_rfies = Rfis.objects.filter(active=True, issue_datetime__date__lte=current_date).exclude(rfi_status="Issued")
        if opened_rfies:
            opened_rfies.update(rfi_status="Opened")
        if issued_rfies:
            issued_rfies.update(rfi_status="Issued")
            rps = RfiParticipationStatus.objects.filter(rfi=issued_rfies.first())
            if rps:
                rps.update(status='Accepted')

    except Exception as e:
        print(e)

    print("Finished update_rfi_status at {}".format(str(datetime.datetime.now())))
