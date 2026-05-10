
#$vms = Import-CSV -Path "C:\test\template\template.csv" -header("Name","Template","PhysicalHost","Datastore","Ipaddr","Netmask","Gateway","Hostname","Esxidir")

$vms = Import-CSV -Path "C:\vmctl\template\whszqh2.csv" -header("user_name","user_username" ,"user_password" ,"asset_ip","gateway" ,"dns" ,"nic_name" ,"template" ,"node","assets_system_name" ,"asset_name")


Connect-VIServer -Protocol https -User 'administrator@vsphere.local' -Password 'Training@321' -Server 192.168.10.200
foreach ($vm in $vms){

get-vm -Name $vm.asset_name | Get-Snapshot -name "snapshot-1"|Remove-Snapshot -confirm:$false
    
}


