#version：v0.1
#env:stage


# 姓名 ,登录名 ,登录密码 ,资产IP  ,网关 ,dns ,网卡名 ,模板名称 ,节点（课程名）,系统用户 ,资产名（主机名）
$vms = Import-CSV -Path "C:\vmctl\template\xh2307-template.csv"  -header("user_name"," user_username"," user_password"," asset_ip"," Gateway"," dns"," nic"," template"," asset_node_name","assets_system_name","asset_name")

$templatenic = 'ens192'
$templateuser = 'root'
$templatepass = 'Asimov'

Connect-VIServer -Protocol https -User 'administrator@vsphere.local' -Password 'Training321@' -Server 192.168.10.200

foreach ($vm in $vms){
      #停止虚拟机
      Get-VM $vm.asset_name| Stop-VM -Confirm:$false
      #Start-Sleep -s 3

      #
      Get-VM $vm.asset_name| Set-VM -MemoryMB 16384 -Confirm:$False 
      Start-Sleep -s 2

      #启动虚拟机
      Get-VM $vm.asset_name| Start-VM

}

