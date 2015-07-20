# kvm_network_initializer

This is a tool that will look at a config file that is specified in conf/config.json and create the KVM image files for all the virtual machine types specified in the config file, while checking if the iso files are present as necessary in the appropriate directory. This is by default 'iso_dir'. If a VMDK file is present in the iso directory, it is used as the disk image for that VM instead of a blank qemu image. All disk images are created in the working directory, which is by default 'working_dir'. A choice of bridge is also available in the config file, and you can either use a Linux Bridge or an OpenVSwitch bridge.

Usage: ./main.py start :for starting VMs and the networks between them.
       ./main.py clean :for destroying networks and VMs.

