from hypervisor import Hypervisor
import os
import socket
import subprocess 
import json
import sys

"""
Class that starts networks and VMs and also destroys them in KVM
"""
class KVM(Hypervisor):
    def __init__(self):
        pass
    
    """
    Function to generate the file that is used by virsh net commands to
    start the networks
    """
    def gen_net_xml(self, sw_name, br_typ):
        f_obj = open('conf/net.xml', 'w')

        f_obj.write('<network>\n')
        
        f_obj.write("\t<name>%s</name>\n" % sw_name)
        f_obj.write("\t<forward mode = 'bridge'/>\n")
        f_obj.write("\t<bridge name = '%s'/>\n" % sw_name)
        
        #Linux Bridge does not require virtualport type to be written in
        if not br_typ == 'LinuxBridge':
            f_obj.write("\t<virtualport type = '%s'/>\n" % br_typ.lower())
    
        f_obj.write("</network>\n")
        f_obj.close()
    
    """
    Function that calls the virsh net commands after creating XML files for
    each network.
    """
    def start_networks(self, br_type):
        f = open('conf/resources.json','r')
        data = json.load(f)
        f.close()

        bridges = []
        for dic in data:
            if 'bridges' in dic.keys():
                for di in dic['bridges']:
                    try:
                        bridges.extend(di.keys())
                    except AttributeError:
                        bridges.append(di)
        
        #Start from 1 because the first field is the type of bridge
        for i in xrange(1,len(bridges)):
            com0 = 'virsh'
            com1 = '--connect'
            com2 = 'qemu:///system'
            
            self.gen_net_xml(bridges[i], br_type)
            subprocess.call([com0,com1,com2,'net-define', 'conf/net.xml'])
            subprocess.call([com0,com1,com2,'net-autostart', bridges[i]])
            subprocess.call([com0,com1,com2,'net-start', bridges[i]])
    
    """
    Function to get an empty TCP port in case the VM is to be connected via
    telnet. To connect to the VM's console via telnet, the port returned
    by this function is used
    """
    def get_port(self, start_port):
        while True:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            res = sock.connect_ex(('', start_port))
            if not res == 0:
                sock.close()
                break
            else:
                start_port += 1
                sock.close()

        return start_port
     
    """
    Function to add the --network set of commands to the virt install 
    commands
    """
    def add_network_and_ext(self, cmd_list, vm):
        for i in vm.connections:
            cmd_list.append('--network')
            cmd_list.append('network=%s,model=e1000' \
            % i)
        
        if 'KVM' in vm.extra_commands.keys():
            for word in vm.extra_commands['KVM'].split():
                cmd_list.append(word)

        return cmd_list
    
    """
    Function to start the VMs using virt-install commands
    """
    def start_vms(self, vm_objs,work_dir, iso_dir):
        used_ports_telnet = []
        i = 1
        start_telnet = 20000
        form = ''
        
        for vm in vm_objs:
            if 'boot_device' in vm.extra_commands.keys():
                if vm.extra_commands['boot_device'] == 'cdrom':
                    vm.extra_commands['KVM'] = '--livecd'

            if 'machine_type' in vm.extra_commands.keys():
                vm.extra_commands['KVM'] += ' --machine=%s' \
                % vm.extra_commands['machine_type']

            if 'cpu_type' in vm.extra_commands.keys():
                vm.extra_commands['KVM'] += ' --cpu qemu64,disable=svm'
 
            if not vm.disk == '':
                form = os.path.splitext(vm.disk)[1]
                form = form[1:]
            else:
                form = 'qcow2'
                subprocess.call(['qemu-img', 'create', '-fqcow2',\
                os.path.join(work_dir,(vm.name+'.img')), '16G'])

                vm.disk = os.path.join(work_dir,vm.name+'.img')
            
            if vm.console == 'telnet':
                tcp_port = get_port(start)
            
                while tcp_port in used_ports:
                    start += 1
                    tcp_port = self.get_port(start)
                    used_ports.append(tcp_port)
        
                cmd_list = [
                'virt-install', 
                '--name=%s' % vm.name, 
                '--ram=1024', 
                '--disk=%s,format=%s,device=disk,bus=ide' % (vm.disk,form), 
                '--disk='+os.path.join(iso_dir,(vm.version+'.iso')),
                ',format=raw,device=cdrom,bus=ide', 
                '--watchdog','i6300esb,action=none']

                cmd_list = self.add_network_and_ext(cmd_list, vm)

                cmd_list.extend(['--graphics', 'none', '--serial',\
                'tcp,host=:%d,mode=bind,protocol=telnet' % tcp_port\
                ,'--noautoconsole'])

                subprocess.call(cmd_list)
                print "%s started with telnet at %d" %(vm.name, tcp_port)

            elif vm.console == 'vnc':
                cmd_list = [
                'virt-install', 
                '--name=%s' % vm.name,
                '--ram=2048',
                '--disk=%s,format=%s,device=disk,bus=ide' % (vm.disk,form),
                '--cdrom=%s' % os.path.join(iso_dir,(vm.version+'.iso')),
                '--watchdog', 'i6300esb,action=none']

                cmd_list = self.add_network_and_ext(cmd_list,vm)
                cmd_list.extend(['--graphics', 'vnc', '--noautoconsole'])
                subprocess.call(cmd_list)
    
    def destroy_networks(self):
        f = open('conf/resources.json', 'r')
        data = json.load(f)
        f.close()
        bridges = []

        for dic in data:
            if 'bridges' in dic.keys():
                bridges = dic['bridges']
        
        com0 = 'virsh'
        com1 = '--connect'
        com2 = 'qemu:///system'

        for i in bridges:
            if type(i).__name__ == 'dict':
                subprocess.call([com0,com1,com2,'net-destroy', i.keys()[0]])
                subprocess.call([com0,com1,com2,'net-undefine',i.keys()[0]])
        
    def destroy_vms(self):
        f = open('conf/resources.json', 'r')
        data = json.load(f)
        f.close()

        for dic in data:
            if 'VMs' in dic.keys():
                for vm in dic['VMs']:
                    subprocess.call(['virsh','destroy', vm])
                    subprocess.call(['virsh','undefine', vm])
