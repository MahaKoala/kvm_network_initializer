#Abstract class from which specific bridge types will inherit.
from abc import ABCMeta, abstractmethod

class Bridge(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def add_bridge(self, *args, **kwargs):
        pass
    
    @abstractmethod
    def del_bridge(self, *args, **kwargs):
        pass
