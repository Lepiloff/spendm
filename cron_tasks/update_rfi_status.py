import datetime
from apps.vendors.models import Rfis


def update_rfi_status():
    print("Started update_rfi_status at {}".format(str(datetime.datetime.now())))

    try:
        current_time = datetime.datetime.now()
        opened_rfies = Rfis.objects.filter(open_datetime__lt=current_time, issue_datetime__gt=current_time).exclude(
            rfi_status="Opened")
        issued_rfies = Rfis.objects.filter(issue_datetime__lte=current_time).exclude(rfi_status="Issued")

        opened_rfies.update(rfi_status="Opened")
        issued_rfies.update(rfi_status="Issued")

    except Exception as e:
        print(e)

    print("Finished update_rfi_status at {}".format(str(datetime.datetime.now())))
