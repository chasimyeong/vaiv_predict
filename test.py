from datetime import datetime
from pytz import timezone

date_today = datetime.now(timezone('Asia/Seoul')).strftime("%Y%m%d%H%M%S")
print('today time : ' + date_today)