# swconf_backup_diff
# version:1.0
# author: zhangzhenhui
# email: 639188185@qq.com

import os
from crontab import CronTab

cron_list =[]
cron_manager = CronTab(user='root')
working_dir = os.getcwd()
for i in cron_manager:
    i = str(i)
    cron_list.append(i)
if '0 21 * * * /bin/python3.9 {0}/swconf_backup.py >> {1}/swconf_backup.log 2>&1 &'.format(working_dir, working_dir) not in cron_list:
    job = cron_manager.new(command='/bin/python3.9 {0}/swconf_backup.py >> /swconf_backup/swconf_backup.log 2>&1 &'.format(working_dir, working_dir))
    job.setall('0 21 * * *')
    cron_manager.write()
print("定时备份配置任务已开启！将在每天21:00开始备份。")