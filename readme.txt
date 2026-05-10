CSV文件模板及字段解释如下：
csv模板 
|user_name|user_username |user_password |asset_ip|gateway |dns |nic_name |template |node 		 |assets_system_name |asset_name 	   |
|姓名	  |   登录名		 |	登录密码		|资产IP	 |网关	  |dns |网卡名	 |模板名称  |节点（课程名）|系统用户 			 |资产名（主机名）  |


v5添加此文件
优化创建菜单功能、优化菜单1，使用菜单1可以完成新建虚拟机时的创建、改IP、创建快照、开机、创建jumpserver用户
添加快照删除和恢复功能
将菜单改为可以持续操作，在完成一个动作后，可以回到主菜单。