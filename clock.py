import pytz
from apscheduler.schedulers.blocking import BlockingScheduler
from datetime import date, datetime
from time import gmtime, strftime

import django

django.setup()

from shopifyRESTfullAPI.views import auto_import
from django.db.models import F
from functions.views import sendOrderEmail
from stock.models import StockItems, Email_schedule

sched = BlockingScheduler()

# original non-timezone time check
# str(strftime("%H:%M", gmtime()))

@sched.scheduled_job('interval', minutes=1)
def timed_job():
    auto_import()
    email = Email_schedule.objects.all()
    dayDic = {'Monday': 0,
              'Tuesday': 1,
              'Wednesday': 2,
              'Thursday': 3,
              'Friday': 4,
              'Saturday': 5,
              'Sunday': 6
              }
    tz = pytz.timezone('Europe/London')
    berlin_now = datetime.now(tz)
    for entry in email:
        stockToOrder = StockItems.objects.filter(company=entry.company, stockAmount__lte=F('orderTrigger'), onOrder=0).filter(allow_reorder=True)
        if date.today().weekday() == dayDic.get(entry.scheduleRun.split('@')[0]):
            if str(berlin_now.strftime("%H:%M")) == str(entry.scheduleRun.split('@')[1]):
                sendOrderEmail(stockToOrder, "Stock To Order", entry.company)

sched.start()
