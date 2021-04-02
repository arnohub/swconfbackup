# swconf_backup_diff
# version:1.0
# author: zhangzhenhui
# email: 639188185@qq.com
from crontab import CronTab

cron_list =[]
cron_manager = CronTab(user='root')
working_dir = os.getcwd()
for i in cron_manager:
    i = str(i)
    cron_list.append(i)
if '0 22 * * * sh /swconf_backup/start.sh' not in cron_list:
    job = cron_manager.new(command='sh /swconf_backup/start.sh')
    job.setall('0 22 * * *')
    cron_manager.write()
print("定时备份配置任务已开启！将在每天22:00开始备份。")
