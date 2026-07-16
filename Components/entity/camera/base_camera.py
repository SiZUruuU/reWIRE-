from abc import ABC, abstractmethod

# ABSTRACT CLASS FOR CAMERA
class BaseCam(ABC):
    def __init__(self, camera, target):
        self.camera = camera
        self.target = target
    
    @abstractmethod
    def scroll(self):
        pass