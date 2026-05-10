from tools import search_for_obj
from tools import connect

from pyVmomi import vim, vmodl
import time
import os

from myclone import execute_program_in_vm
from myclone import create_snapshot
from myclone import clone_vm
from myclone import destroy_vm
from myclone import operation_snapshot
from myclone import powerOn,powerOff

import jumpserver1 as jms


def createVMmain(vm_folder='', cluster_name='vm-cluster', real_datastore_name='Datacenter',
                 datacenter_name='Datacenter', datastore_name='', resource_pool='', power_on=True,
                 datastorecluster_name=''):
    # 创建虚拟机
    print('\n\n 开始创建虚拟机...')
    for row0 in rows:
        row = row0.split(',')
        if '姓名' in row[0]:
            continue
        # ==============================================
        vm_name = row[10]  # 资产名
        template = row[7]  # 模板名称

        # 创建虚拟机
        template = search_for_obj(content, [vim.VirtualMachine], template)
        if template:
            clone_vm(content, template, vm_name, datacenter_name, vm_folder,
                     datastore_name, cluster_name, resource_pool, power_on,
                     datastorecluster_name)
        else:
            print("template not found")


def createJMP():
    print('\n\n 开始创建jumpserver用户...')
    for row0 in rows:
        row = row0.split(',')
        if '姓名' in row[0]:
            continue
        # 用户用户名
        user_name = row[0].strip()  # 姓名
        user_username = row[1].strip()  # 登录名
        user_password = row[2].strip()  # 用户密码
        asset_ip = row[3].strip()  # 资产IP
        asset_node_name = row[8].strip()  # 资产节点
        assets_system_name = row[9].strip()  # 资产系统用户
        asset_name = f'{row[10]}'  # 资产名
        # 创建jumpserver用户
        print(user_name, user_username, user_password, asset_ip, asset_node_name, assets_system_name, asset_name)
        jms.main(user_name, user_username, user_password, asset_ip, asset_node_name, assets_system_name, asset_name)


def changeIpmain(vm_user='root', vm_pwd='Asimov'):
    print('\n\n 开始修改IP...')
    for row0 in rows:
        row = row0.split(',')
        if '姓名' in row[0].strip():
            continue
        vm_name = row[10].strip()  # 资产名
        nic_name = row[6].strip()  # 'ens192'
        ipaddr = row[3].strip()  # '172.31.200.34'
        gateway = row[4].strip()  # '172.31.0.254'
        dns = row[5].strip()  # '172.31.0.248'
        print(nic_name, ipaddr, gateway, dns, vm_name, '================')

        # ------------------------------------------------
        programPath = f'/usr/bin/nmcli'

        arguments = f'''connection modify {nic_name} ipv4.method manual ipv4.addresses {ipaddr}/16 ;\
		nmcli connection modify {nic_name} ipv4.gateway {gateway};\
		nmcli connection modify {nic_name} ipv4.dns {dns};\
		nmcli connection modify {nic_name} autoconnect yes;\
		nmcli connection  up {nic_name}; \
        hostnamectl set-hostname {vm_name}.training.com;
		'''
        # ==================================================

        # 执行命令设置IP和主机名，不能在创建虚拟机后马上运行，虚拟机没有完全启动，执行命令报错
        execute_program_in_vm(content, vm_name, vm_user, vm_pwd, programPath, arguments)
        time.sleep(0.5)
        # programPath = f'/bin/hostnamectl'
        # arguments = f'set-hostname {vm_name}.training.com;'

        # time.sleep(0.5)

def changeIpmain1(vm_user='administrator', vm_pwd='Admin@123'):
    print('\n\n 开始修改windows IP...')
    for row0 in rows:
        row = row0.split(',')
        if '姓名' in row[0].strip():
            continue
        vm_name = row[10].strip()  # 资产名
        nic_name = row[6].strip()  # 'ens192'
        ipaddr = row[3].strip()  # '172.31.200.34'
        gateway = row[4].strip()  # '172.31.0.254'
        dns = row[5].strip()  # '172.31.0.248'
        print(nic_name, ipaddr, gateway, dns, vm_name, '================')

        # ------------------------------------------------
        programPath = r'C:\Windows\System32\netsh.exe'
        arguments = f'''interface ip set address name="{nic_name}" static {ipaddr} 255.255.0.0 {gateway}'''
        # netsh interface ip set dns name="{nic_name}" static {dns};
        # ==================================================

        # 执行命令设置IP和主机名，不能在创建虚拟机后马上运行，虚拟机没有完全启动，执行命令报错
        execute_program_in_vm(content, vm_name, vm_user, vm_pwd, programPath, arguments)
        time.sleep(1)


def createSnapMain(sname='snapshot-1', description=time.asctime()):
    print('\n\n 开始创建快照...')
    sname = sname if sname else 'snapshot-1'
    for row0 in rows:
        row = row0.split(',')
        if '姓名' in row[0].strip():
            continue
        vm_name = row[10].strip()  # 资产名

        # 创建快照
        create_snapshot(content, vm_name, sname, description)


def destroyVM(asset_name=''):
    print('\n\n 开始删除虚拟机...')
    if asset_name:  # 删除单个虚拟机
        destroy_vm(content, asset_name)
    else:  # 批量删除
        for row0 in rows:
            row = row0.split(',')

            if '姓名' in row[0]:
                continue
            asset_name = row[10].strip()  # 资产名
            destroy_vm(content, asset_name)

def destroySnap(asset_name='',sname = ''):
    sname = sname if sname else 'snapshot-1'
    if asset_name :
        operation_snapshot(content, vm_name=asset_name,snapshot_name=sname,snapshot_operation='remove')
    else:
        for row0 in rows:
            row = row0.split(',')

            if '姓名' in row[0]:
                continue
            asset_name = row[10].strip()  # 资产名
            operation_snapshot(content, vm_name=asset_name,snapshot_name=sname,snapshot_operation='remove')

def revertSnap(asset_name='', sname=''):
    sname = sname if sname else 'snapshot-1'
    if asset_name :
        operation_snapshot(content, vm_name=asset_name,snapshot_name=sname,snapshot_operation='revert')
    else:
        for row0 in rows:
            row = row0.split(',')

            if '姓名' in row[0]:
                continue
            asset_name = row[10].strip()  # 资产名
            operation_snapshot(content, vm_name=asset_name,snapshot_name=sname,snapshot_operation='revert')

def powerOnvm(asset_name):
    if asset_name :
        powerOn(content, vm_name=asset_name)
    else:
        for row0 in rows:
            row = row0.split(',')

            if '姓名' in row[0]:
                continue
            asset_name = row[10].strip()  # 资产名
            powerOn(content, vm_name=asset_name)

def powerOffvm(asset_name):
    if asset_name :
        powerOn(content, vm_name=asset_name)
    else:
        for row0 in rows:
            row = row0.split(',')

            if '姓名' in row[0]:
                continue
            asset_name = row[10].strip()  # 资产名
            powerOff(content, vm_name=asset_name)



filename = input(''' 
请输入一个CSV文件的路径。csv文件模板请参照readme.txt文件。注意文件路径中不要带有引号。
>>>''')

if os.path.exists(filename):
    pass
else:
    raise SystemExit("这个文件不存在吧！！！")

#############公共变量###################################
with open(filename, encoding='utf8') as f:
    rows = f.readlines()

#############公共变量###################################
# +++连接vcenter+++++++++++++++++++++++++++++++++++++++
si = connect()
content = si.RetrieveContent()
#############公共变量结束##############################

while True:
     
    action = input('''
    1、创建虚拟机+修改IP+创建快照
    2、删除虚拟机
    3、修改IP
    4、创建快照
    5、创建虚拟机
    6、创建jumpserver用户
    7、恢复快照
    8、删除快照
    9、开机
    10、关机

    退出请输入exit

    输入编号>>>''')

    if action == '1':
        # 1、创建虚拟机+修改IP+创建快照+创建jumpserver用户
        createVMmain()
        # createJMP()
        changeIpmain()
        powerOffvm(asset_name='')
        createSnapMain()

    elif action == '2':
        # 2、删除所有虚拟机
        vmname = input('输入要删除的虚拟机名，【默认删除文件中所有虚拟机】：')
        destroyVM(asset_name=vmname)

    elif action == '3':
        # 3、修改IP
        changeIpmain()
    elif action == '4':
        # 4、创建快照
        sname=input('输入要创建的快照名，【默认快照名"snapshot-1"】：')
        createSnapMain(sname=sname)

    elif action == '5':
        # 5、创建虚拟机
        createVMmain()

    # elif action == '6':
    #     createJMP()

    elif action == '7':
        asset_name=input('输入要恢复快照的虚拟机名，【默认恢复文件中所有虚拟机】：')
        sname=input('输入要恢复的快照名，【默认恢复到"snapshot-1"】：')
        revertSnap(asset_name,sname)
        
    elif action == '8':
        asset_name=input('输入要删除快照的虚拟机名，【默认删除文件中所有虚拟机】：')
        sname=input('输入要删除的快照名，【默认删除"snapshot-1"】：')
        destroySnap(asset_name,sname)

    elif action == '9':
        asset_name=input('输入要打开的虚拟机名，【默认打开文件中所有虚拟机】：')
        powerOnvm(asset_name)

    elif action == '10':
        asset_name=input('输入要关闭的虚拟机名，【默认关闭文件中所有虚拟机】：')
        powerOffvm(asset_name)

    elif action == 'exit':
        break
    else:
        print('\n\n输错了吧！请重新按提示输入')
