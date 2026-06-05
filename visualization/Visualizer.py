from abc import ABC, abstractmethod

class Visualizer(ABC):

    @abstractmethod
    def run(self):
        pass
  