from abc import ABC, abstractmethod

from power_monitoring_plug import PowerMonitoringPlug


class IntelligentPlug(ABC):

    @abstractmethod
    def get_backend(self) -> PowerMonitoringPlug:
        pass

    @abstractmethod
    def update(self) -> None:
        pass
