import datetime
from apps.vendors.models import Rfis


def update_rfi_status():
    print("Started update_rfi_status at {}".format(str(datetime.datetime.now())))

    try:
        current_date = datetime.datetime.today()
        opened_rfies = Rfis.objects.filter(active=True, open_datetime__date__lt=current_date,
                                           issue_datetime__date__gt=current_date).exclude(
            rfi_status="Opened")
        issued_rfies = Rfis.objects.filter(active=True, issue_datetime__date__lte=current_date).exclude(rfi_status="Issued")

        opened_rfies.update(rfi_status="Opened")
        issued_rfies.update(rfi_status="Issued")

    except Exception as e:
        print(e)

    print("Finished update_rfi_status at {}".format(str(datetime.datetime.now())))
