# kvm_network_initializer

This is a script that will look at a config file that is specified, by default in conf/config.json and create the KVM image files for all the virtual machine types specified in the config file, while checking if the iso files are present as necessary in the appropriate directory. There are two types of virtual machines, switchvm and hostvm. 

  Then, looking at the connections section of the config file, it will create networks between these virtual machines using the 'virsh' commands of KVM.
