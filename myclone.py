from pyVmomi import vim, vmodl
import time
import re
from tools import search_for_obj
from tools import wait_for_task
from pyVim.task import WaitForTask
# from tools import connect
from tools import get_all_obj
from tools import get_snapshots_by_name_recursively


# 克隆虚拟机
def clone_vm(content, template, vm_name, datacenter_name, vm_folder, datastore_name,
             cluster_name, resource_pool, power_on, datastorecluster_name):
    """
    Clone a VM from a template/VM, datacenter_name, vm_folder, datastore_name
    cluster_name, resource_pool, and power_on are all optional.
    """

    # if none git the first one
    datacenter = search_for_obj(content, [vim.Datacenter], datacenter_name)

    if vm_folder:
        destfolder = search_for_obj(content, [vim.Folder], vm_folder)
    else:
        destfolder = datacenter.vmFolder

    if datastore_name:
        datastore = search_for_obj(content, [vim.Datastore], datastore_name)
    else:
        datastore = search_for_obj(
            content, [vim.Datastore], template.datastore[0].info.name)

    # if None, get the first one
    cluster = search_for_obj(content, [vim.ClusterComputeResource], cluster_name)
    if not cluster:
        clusters = get_all_obj(content, [vim.ResourcePool])
        cluster = list(clusters)[0]

    if resource_pool:
        resource_pool = search_for_obj(content, [vim.ResourcePool], resource_pool)
    else:
        resource_pool = cluster.resourcePool

    vmconf = vim.vm.ConfigSpec()

    if datastorecluster_name:
        podsel = vim.storageDrs.PodSelectionSpec()
        pod = search_for_obj(content, [vim.StoragePod], datastorecluster_name)
        podsel.storagePod = pod

        storagespec = vim.storageDrs.StoragePlacementSpec()
        storagespec.podSelectionSpec = podsel
        storagespec.type = 'create'
        storagespec.folder = destfolder
        storagespec.resourcePool = resource_pool
        storagespec.configSpec = vmconf

        try:
            rec = content.storageResourceManager.RecommendDatastores(
                storageSpec=storagespec)
            rec_action = rec.recommendations[0].action[0]
            real_datastore_name = rec_action.destination.name
        except Exception:
            real_datastore_name = template.datastore[0].info.name

        datastore = search_for_obj(content, [vim.Datastore], real_datastore_name)

    # set relospec
    relospec = vim.vm.RelocateSpec()
    relospec.datastore = datastore
    relospec.pool = resource_pool

    clonespec = vim.vm.CloneSpec()
    clonespec.location = relospec
    clonespec.powerOn = power_on

    print(f"\n cloning VM {vm_name}...")
    task = template.Clone(folder=destfolder, name=vm_name, spec=clonespec)
    wait_for_task(task)
    print("VM cloned.")

# 虚拟机关机
def power_offvm():
    pass

# 执行脚本  设置IP和主机名
def execute_program_in_vm(content, vm_name, vm_user, vm_pwd, programPath, arguments=''):
    """
    Simple command-line program for executing a process in the VM without the
    network requirement to actually access it.
    """

    try:
        vm = None
        if vm_name:
            vm = search_for_obj(content, [vim.VirtualMachine], vm_name)
        if not vm:
            raise SystemExit("Unable to locate the virtual machine.")

        tools_status = vm.guest.toolsStatus

        ttl = 5
        while tools_status in ('toolsNotInstalled', 'toolsNotRunning'):
            print('wait VMwareTools running...')
            time.sleep(2)
            ttl -= 1
            tools_status = vm.guest.toolsStatus
            if ttl == 0:
                break

        if tools_status in ('toolsNotInstalled', 'toolsNotRunning'):
            raise SystemExit(
                "VMwareTools is either not running or not installed. "
                "Rerun the script after verifying that VMwareTools "
                "is running")

        creds = vim.vm.guest.NamePasswordAuthentication(
            username=vm_user, password=vm_pwd
        )

        try:
            profile_manager = content.guestOperationsManager.processManager

            if arguments:
                program_spec = vim.vm.guest.ProcessManager.ProgramSpec(
                    programPath=programPath,
                    arguments=arguments)
            else:
                program_spec = vim.vm.guest.ProcessManager.ProgramSpec(
                    programPath=programPath)

            res = profile_manager.StartProgramInGuest(vm, creds, program_spec)
            print(res)

            # if res > 0:
            #     print("Program submitted, PID is %d" % res)
            #     pid_exitcode = \
            #         profile_manager.ListProcessesInGuest(vm, creds, [res]).pop().exitCode
            #     # If its not a numeric result code, it says None on submit
            #     while re.match('[^0-9]+', str(pid_exitcode)):
            #         print("Program running, PID is %d" % res)
            #         time.sleep(2)
            #         pid_exitcode = \
            #             profile_manager.ListProcessesInGuest(vm, creds, [res]).pop().exitCode
            #         if pid_exitcode == 0:
            #             print("Program %d completed with success" % res)
            #             break
            #         # Look for non-zero code to fail
            #         elif re.match('[1-9]+', str(pid_exitcode)):
            #             print("ERROR: Program %d completed with Failute" % res)
            #             print("  tip: Try running this on guest %r to debug"
            #                   % vm.summary.guest.ipAddress)
            #             print("ERROR: More info on process")
            #             print(profile_manager.ListProcessesInGuest(vm, creds, [res]))
            #             break

        except IOError as ex:
            print(ex)
    except vmodl.MethodFault as error:
        print("Caught vmodl fault : " + error.msg)
        return -1
    time.sleep(1)
    # task = vm.PowerOff()
    # wait_for_task(task)
    return 0


# 创建快照 
def create_snapshot(content, vm_name, sname, description):
    instance_search = False
    vm = search_for_obj(content, [vim.VirtualMachine], vm_name)

    if vm is None:
        raise SystemExit("Unable to locate VirtualMachine.")

    desc = None if description is None else description

    task = vm.CreateSnapshot_Task(name=sname,
                                  description=desc,
                                  memory=True,
                                  quiesce=False)
    print('create snapshot...')
    wait_for_task(task)
    print("Snapshot Completed.")
    # del vm
    # vm = content.searchIndex.FindByUuid(None, uuid, True, instance_search)

    snap_info = vm.snapshot

    tree = snap_info.rootSnapshotList
    while tree[0].childSnapshotList is not None:
        print("Snap: {0} => {1}".format(tree[0].name, tree[0].description))
        if len(tree[0].childSnapshotList) < 1:
            break
        tree = tree[0].childSnapshotList

    tasks = vm.PowerOn()
    # Wait for power on to complete
    print(f'poweron {vm.name} ...')
    wait_for_task(tasks)
    print("poweron done")

# 开机
def powerOn(content, vm_name):
    instance_search = False
    vm = search_for_obj(content, [vim.VirtualMachine], vm_name)

    if vm is None:
        raise SystemExit("Unable to locate VirtualMachine.")
    tasks = vm.PowerOn()
    # Wait for power on to complete
    print(f'poweron {vm.name} ...')
    wait_for_task(tasks)
    print("poweron done")

# 关机
def powerOff(content, vm_name):
    instance_search = False
    vm = search_for_obj(content, [vim.VirtualMachine], vm_name)

    if vm is None:
        raise SystemExit("Unable to locate VirtualMachine.")
    tasks = vm.PowerOff()
    # Wait for power on to complete
    print(f'poweroff {vm.name} ...')
    wait_for_task(tasks)
    print("poweroff done")


# 恢复快照,删除快照
def operation_snapshot(content, vm_name, snapshot_name,snapshot_operation):
    instance_search = False
    vm = search_for_obj(content, [vim.VirtualMachine], vm_name)

    if vm is None:
        raise SystemExit("Unable to locate VirtualMachine.")

    snap_obj = get_snapshots_by_name_recursively(
                            vm.snapshot.rootSnapshotList, snapshot_name)
        # if len(snap_obj) is 0; then no snapshots with specified name
    if len(snap_obj) == 1:
        snap_obj = snap_obj[0].snapshot
        if snapshot_operation == 'remove':
            print("Removing snapshot %s" % snapshot_name)
            WaitForTask(snap_obj.RemoveSnapshot_Task(True))
        elif snapshot_operation == 'revert':
            print("Reverting to snapshot %s" % snapshot_name)
            WaitForTask(snap_obj.RevertToSnapshot_Task())
        else:
            print(f"Inpute error")
    else:
        print("No snapshots found with name: %s on VM: %s" % (
                                                snapshot_name, vm.name))




# 删除虚拟机
def destroy_vm(content, vm_name):
    VM = search_for_obj(content, [vim.VirtualMachine], vm_name)

    if VM is None:
        raise SystemExit(f"Unable to locate VirtualMachine {vm_name}. ")

    print("Found: {0}".format(VM.name))
    print("The current powerState is: {0}".format(VM.runtime.powerState))

    if format(VM.runtime.powerState) == "poweredOn":
        print("Attempting to power off {0}".format(VM.name))
        TASK = VM.PowerOffVM_Task()
        wait_for_task(TASK)
        print("{0}".format(TASK.info.state))

    print("Destroying VM from vSphere.")
    TASK = VM.Destroy_Task()
    wait_for_task(TASK)
    print("Done.")


"""
def main():
    # ==============================================
    vm_name='python-test4'
    template='centos7-mini'

    vm_folder=''
    cluster_name='Cluster-A'
    real_datastore_name='vsanDatastore-1'
    datacenter_name='Datacenter'
    datastore_name=''
    resource_pool=''
    power_on=True
    datastorecluster_name=''

    # ++++++++++++++++++++++++++++++++++++++++++++++++++
    # 配置IP和主机名
    vm_user='root'
    vm_pwd = 'Asimov'


    nic_name = 'ens192'
    ipaddr = '172.31.200.34/16'
    gateway = '172.31.0.254'
    dns = '172.31.0.248'

    # ------------------------------------------------
    programPath = f'/usr/bin/nmcli'

    arguments=f'''connection modify {nic_name} ipv4.method manual ipv4.addresses {ipaddr}/16 ;\
    nmcli connection modify {nic_name} ipv4.gateway {gateway};\
    nmcli connection modify {nic_name} ipv4.dns {dns};\
    nmcli connection modify {nic_name} autoconnect yes;\
    nmcli connection  up {nic_name};
    sed -i  "s#.*#{vm_name}.training.com#" /etc/hostname;
    init 0
    '''
    # ++++++++++++++++++++++++++++++++++++++++++++++++++
    # 快照
    sname = 'snapshot'
    description = time.asctime()


    #==================================================
    si = connect()
    content = si.RetrieveContent()
    #==================================================
    # 创建虚拟机
    template = search_for_obj(content, [vim.VirtualMachine], template)
    if template:
        clone_vm(
            content, template, vm_name, datacenter_name, vm_folder,
            datastore_name, cluster_name, resource_pool, power_on,
            datastorecluster_name)
    else:
        print("template not found")


    # 执行命令设置IP和主机名，不能在创建虚拟机后马上运行，虚拟机没有完全启动，执行命令报错
    execute_program_in_vm(content,vm_name,vm_user,vm_pwd,programPath, arguments)

    # 创建快照
    create_snapshot(content,vm_name,sname,description)



# # Start program
if __name__ == "__main__":
    

    main()

"""
