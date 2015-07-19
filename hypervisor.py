#Abstract class from which specific hypervisor types will inherit.
from abc import ABCMeta, abstractmethod

class Hypervisor(object):
    @abstractmethod
    def check_and_start_network(self, *args, **kwargs):
        pass

    @abstractmethod
    def start_vms(self, *args, **kwargs):
        pass

    @abstractmethod
    def destroy_network(self, *args, **kwargs):
        pass

    @abstractmethod
    def destroy_vms(self, *args, **kwargs):
        pass
