from abc import ABC, abstractmethod

# ABSTRACT CLASS FOR CAMERA
class BaseCam(ABC):
    def __init__(self, camera, target):
        self.camera = camera
        self.target = target
    
    # method to use to define how the camera moves
    @abstractmethod
    def scroll(self, delta_time):
        pass