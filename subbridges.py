from bridge import Bridge
import subprocess

#Bridge classes that add and delete bridges.
class LinuxBridge(Bridge):
    def __init__(self, name):
        self.name = name

    def add_bridge(self):
        subprocess.call(['brctl', 'addbr', self.name])

    def del_bridge(self):
        subprocess.call(['brctl', 'delbr', self.name])

class OVSBridge(Bridge):
    def __init__(self, name):
        self.name = name

    def add_bridge(self):
        subprocess.call(['ovs-vsctl', 'add-br', self.name])

    def del_bridge(self):
        subprocess.call(['ovs-vsctl', 'del-br', self.name])
