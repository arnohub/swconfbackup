# swconf_backup_diff
# version:1.0
# author: zhangzhenhui
# email: 639188185@qq.com

from netmiko import ConnectHandler
import os
import datetime
import filecmp
import threading
import difflib
import settings
import smtplib
from email.mime.text import MIMEText
from email.header import Header


####Setting maxmum threading number#####
threads_max_num = 20
########################################

dev_dict = {}
dev_list = []
dev_map = {}
idc_name = ''
device_type = ''
dev_name =''
host = ''
conffile_name = ''
confdir = ''
errlist = []
nochange_device = []
change_device = []

class ConfigSwitch(object):
    def __init__(self):
        global conffile_name
        conffile_name = dev_map['host'] + '_hellobike.cfg'
        self.conffile_dir = confdir + '/' + conffile_name
        if os.path.exists(self.conffile_dir):
            os.remove(self.conffile_dir)
        self.conffile = open(self.conffile_dir, 'a+')

    def get_config(self, dev_map):
        print('Device:{0} is backuping up...'.format(dev_map['host']))
        try:
            self.net_connect = ConnectHandler(**dev_map)
            save_cmds = settings.save_command
            output = self.net_connect.send_command("dis cur")
            self.net_connect.send_config_set(save_cmds)
            self.conffile.writelines(output)
        except:
            nowtime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            nowdate = datetime.date.today().strftime("%Y%m%d")
            print('Unable to connect to device: {}，LOG: {}'.format(dev_map['host'], os.getcwd() + '/' + settings.idc + '/' + nowdate + '/errlist'))
            global errlist
            errlist.append(dev_map['host'])
            with open(os.getcwd() + '/' + settings.idc + '/' + nowdate + '/errlist', 'a+') as err:
                err.writelines('\n{0} Backup failed device: {1}'.format(nowtime, dev_map['host']))
        print('Device:{0} is Done.'.format(dev_map['host']))
        print('#####################################')

def get_dev_info(dev_file):
    nowdate = datetime.date.today().strftime("%Y%m%d")
    global confdir
    confdir = os.getcwd() + '/' + settings.idc + '/' + nowdate
    if not os.path.exists(confdir):
        os.makedirs(confdir)
    try:
        with open(dev_file, 'r') as devices:
            global dev_dict
            global dev_list
            global device_type
            global dev_map
            global dev_name
            for i in devices:
                block_flag = False
                i = i.split()
                dev_os = i[3]
                dev_role = i[2]
                dev_ip = i[1]
                dev_name = i[0]
                login_port = 22
                login_secret = ''
                login = settings.username
                pwd = settings.password
                if len(i) > 4:
                    login = i[4]
                    pwd = i[5]
                for type in settings.block_role:
                    if type in dev_name:
                        block_flag = True
                if not block_flag:
                    key_name = ("device_type", "host", "username", "password", "port", "secret")
                    values = (dev_os, dev_ip, login, pwd, login_port, login_secret)
                    dev_dict = dict(zip(key_name, values))
                    dev_list.append(dev_dict)
    except:
        print("Could not open devlist file, please check the file: {0}/devlist".format(os.getcwd()))
    threads = []
    n = 1
    for dev_map in dev_list:
        threads.append(threading.Thread(target=ConfigSwitch().get_config, args=(dev_map, )))
        if n % threads_max_num == 0:
            for t in threads:
                t.start()
            for t in threads:
                t.join()
            threads = []
        n = n + 1
        if n - 1 == len(dev_list):
            for t in threads:
                t.start()
            for t in threads:
                t.join()

def conf_diff():
    global nochange_device
    global change_device
    today = datetime.date.today()
    oneday = datetime.timedelta(days=1)
    yestarday = today - oneday
    yestarday_dir = os.getcwd() + '/' + settings.idc + '/' + yestarday.strftime("%Y%m%d") + '/'
    today_dir = os.getcwd() + '/' + settings.idc + '/' + today.strftime("%Y%m%d") + '/'
    today_conf = os.listdir(today_dir)
    for i in today_conf:
        if '_hellobike.cfg' not in i:
            today_conf.pop(today_conf.index(i))
    for conf_file in today_conf:
        if os.path.exists(yestarday_dir + conf_file):
            result = filecmp.cmp(today_dir + conf_file, yestarday_dir + conf_file, shallow=True)
            if not result:
                if conf_file.split('_')[0] not in errlist:
                    change_device.append(conf_file)
                    with open(today_dir + conf_file, 'r') as newfile, open(yestarday_dir + conf_file, 'r') as oldfile:
                        diff_results = list(difflib.ndiff(oldfile.readlines(), newfile.readlines()))
                        with open(os.getcwd() + '/report/' + today.isoformat() + '_report', 'a+') as report_file:
                            alias = '\n############设备: {0} 发生以下配置变化############\n'.format(conf_file.strip('_hellobike.cfg'))
                            report_file.writelines(alias)
                            try:
                                for index, line in enumerate(diff_results):
                                    if line.startswith(('+ ', '- ')):
                                        alias = '配置发生变化: {0}'.format(line)
                                        report_file.writelines(alias)
                                    if line.startswith('? '):
                                        alias = '具体变动位置: {0}'.format(line)
                                        report_file.writelines(alias)
                                    else:
                                        pass
                            except:
                                pass
                else:
                    with open(os.getcwd() + '/report/' + today.isoformat() + '_report', 'a+') as report_file:
                        alias = '以下设备配置备份失败:\n{}\n\n\n'.format('\n'.join(errlist))
                        report_file.writelines(alias)
            else:
                nochange_device.append(conf_file)
        else:
            with open(os.getcwd() + '/report/' + today.isoformat() + '_report', 'a+') as report_file:
                alias = '新增配置文件:{}'.format(conf_file)
                report_file.writelines(alias)
    if not os.path.exists(os.getcwd() + '/report/' + today.isoformat() + '_report'):
        f = open(os.getcwd() + '/report/' + today.isoformat() + '_report', 'a+')
        f.close()
        # os.mknod(os.getcwd() + '/report/' + today.isoformat() + '_report')
        with open(os.getcwd() + '/report/' + today.isoformat() + '_report', 'r+') as report_file:
            report_file.seek(0, 0)
            content = report_file.read()
            alias = '\n\n############################################\n成功备份所有设备，共计{}台，未发现配置变动\n############################################\n\n'.format(len(today_conf))
            report_file.write(alias + content)
    else:
        with open(os.getcwd() + '/report/' + today.isoformat() + '_report', 'r+') as report_file:
            report_file.seek(0, 0)
            content = report_file.read()
            alias = '\n\n#######################################################\n成功备份{0}台设备，{1}台设备备份失败，{2}台设备配置发生变动\n#######################################################\n\n'.format(len(today_conf), len(errlist), len(change_device))
            report_file.write(alias + content)

def send_mail():
        sender = "639188185@qq.com"
        recevers = "639188185@qq.com"
        username = '639188185@qq.com'
        password = 'passwd'
        smtpserver = 'smtp.qq.com'
        today = datetime.date.today()
        try:
            with open(os.getcwd() + '/report/' + today.isoformat() + '_report', 'r') as file:
                mail_body = file.read()
                msg = MIMEText(mail_body, 'plain', 'utf-8')
                msg['Subject'] = Header('{} 交换机配置变动每日报告'.format(today), 'utf-8')
                # msg['From'] = Header('639188185@qq.com"', 'utf-8')
                msg['From'] = '639188185@qq.com"'
                for i in recevers.split(','):
                    msg['To'] = i
                smtp = smtplib.SMTP()
                smtp.connect(smtpserver, 25)
                smtp.login(username, password)
                smtp.send_message(msg, sender, recevers.split(','))
                smtp.quit()
        except smtplib.SMTPException:
            print('邮件发送失败')

if __name__ == '__main__':
    get_dev_info(os.getcwd() + '/devlist')
    conf_diff()
    send_mail()