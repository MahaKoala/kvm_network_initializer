#!/usr/bin/env python
import subprocess
import json
from vm import VM
import argparse

"""
Main script that uses appropriate objects to start and destroy VMs and network topologies between them.
"""

iso_dir = 'iso_dir'
work_dir = 'working_dir'

def start_bridges(bridge_type, connections):
    """
    Import the bridge which is specified in the config file using getattr
    """
    mod = __import__('subbridges')
    mod = getattr(mod,bridge_type)
    
    mod('mgmt').add_bridge()
    mod('dummy').add_bridge()
    
    for key in connections:
        mod(key).add_bridge()
    
def cleanup():
    f = open('conf/resources.json','r')
    data = json.load(f)
    f.close()
    
    mod_br = __import__('subbridges')
    mod_hyp = __import__('subhypervisors')
    for dic in data:
        if 'hypervisor' in dic.keys():
            mod_hyp = getattr(mod_hyp, dic['hypervisor'])
    
    hyp = mod_hyp()
    
    for dic in data:
        if 'bridges' in dic.keys():
            mod_br = getattr(mod_br,dic['bridges'][0])
            for item in dic['bridges']:
                destroyable = ''
                if type(item).__name__ == 'dict':
                    destroyable = item.keys()[0]
                    mod_br(destroyable).del_bridge()
    
    hyp.destroy_networks()
    hyp.destroy_vms()

def main():
    f = open('conf/config.json','r')
    f2 = open('conf/options.json', 'r')
    data = json.load(f)
    data2 = json.load(f2)
    f.close()
    f2.close()
    bridge_list = hypervisor_list = []
    vm_list = []
    connections = {}

    for dic in data2:
        if 'COMMON' in dic.keys():
            bridge_list = dic['COMMON']['BRIDGES']
            hypervisor_list = dic['COMMON']['HYPERVISOR']
            
    brdige_type = hypervisor_type = ''
    
    for dic in data:
        if 'COMMON' in dic.keys():
            bridge_type = dic['COMMON']['BRIDGE'] 
            if not bridge_type in bridge_list:
                print ('Invalid bridge, list of valid bridges are:')
                for i in bridge_list:
                    print (i)

            hypervisor_type = dic['COMMON']['HYPERVISOR']
            if not hypervisor_type in hypervisor_list:
                print ('Invalid Hypervisor, list of valid \
                hypervisors are:')
                for i in hypervisor_list:
                    print (i)
        
        if 'VMS' in dic.keys():
            for vm in dic['VMS']:
                vm_list.append(vm)

        if 'CONNECTIONS' in dic.keys():
            connections = dic['CONNECTIONS']
    
    vm_obj_dict = {}
    
    for i in xrange(len(vm_list)):
        vm_obj_dict[vm_list[i]['name']] = (VM(vm_list[i],iso_dir,work_dir))

    for key in connections:
        conn_name = key
        for endp in connections[key]:
            if endp['name'] in vm_obj_dict.keys():
                vm_obj_dict[endp['name']].fill_connection(endp,conn_name)
    
    f = open('conf/resources.json','w')
    writable = []
    writable.append({'bridges':[bridge_type]})
    writable.append({"hypervisor":hypervisor_type})

    writable[0]['bridges'].extend(['mgmt', 'dummy'])
    for key in connections:
        writable[0]['bridges'].append({key:connections[key]})
    
    json.dump(writable,f)
    f.close()
    
    HyperVisor = __import__('subhypervisors')
    HyperVisor = getattr(HyperVisor, hypervisor_type)

    hyp = HyperVisor()
    start_bridges(bridge_type, connections)
    hyp.start_networks(bridge_type)
    
    vm_obj_list = [vm_obj_dict[key] for key in vm_obj_dict]
    
    hyp.start_vms(vm_obj_list, work_dir, iso_dir)
    
    f = open('conf/resources.json','r')
    data = json.load(f)
    f.close()

    f = open('conf/resources.json', 'w')
    
    data.append({"VMs":[]})

    for dic in data:
        if "VMs" in dic.keys():
            for vm in vm_obj_list:
                dic['VMs'].append(vm.name)
    
    json.dump(data,f)
    f.close()

parser = argparse.ArgumentParser()
parser.add_argument("action", help="Action to be taken, Options are:\n"+
                    "'start', 'clean', 'console'")
parser.add_argument("--name", help="VM name to connect to if console"+\
                    " option is specified")

args = parser.parse_args()

if args.action == 'start':
    main()
elif args.action == 'clean':
    cleanup() 

