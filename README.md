# swconfbackup

## 软件介绍

自动定时备份交换机(ssh)，默认开20个线程，实测线程超过25个概率性存在备份失败的情况，建议保持默认，settings.py 里设定设备角色，机房，需要屏蔽某类型的设备，通用账户等信息，如遇到某些设备使用特殊账户，只需要在devlist设备列表中指定即可，swconf_backup.py 执行完配置备份后会使用difflib模块对比前一天的配置，将diff结果默认发送给指定邮件

setTask.py 为定时执行脚本，每天凌晨2:00执行备份任务，可根据实际需求更改，建议在设备压力低峰期执行。

Automatic daily scheduled backup of switch and router configuration, support H3C、HUAWEI

After the backup, the configuration will be saved automatically 

## settings.py

Set the IDC, device role, roles without backup, login username and password, etc

you can set the account shared by all equipment.

## devlist

Yeah, device lists, as shown below. If all devices shared the same account, you can set in settings.py 

*sysname, mgtip, device role, os, username(optional), password(optional;)*

## swconf_backup.py

main script

## setTask.py

Scheduling Jobs with python-crontab

## 使用方法：

pip3.9 install python-crontab -i http://pypi.douban.com/simple --trusted-host pypi.douban.com

pip3.9 install netmiko -i http://pypi.douban.com/simple --trusted-host pypi.douban.com

pip3.9 install email==6.0.0a1 -i http://pypi.douban.com/simple --trusted-host pypi.douban.com

python3.9 setTask.py 开启定时备份任务

python3.9 swconf_backup.py 立即开始备份，对比配置并发送邮件（测试使用）

## 效果展示

![image](https://github.com/arnohub/swconfbackup/blob/main/swconfbackup/example1.jpg)
![image](https://github.com/arnohub/swconfbackup/blob/main/swconfbackup/example2.jpg)

## 联系方式

If you have any problems or questions with swconfbackup, please contact me WeChat:zkpws2010 email:639188185@qq.com
