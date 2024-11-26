from abc import ABC, abstractmethod


class PowerMonitoringPlug(ABC):

    @abstractmethod
    def get_power(self) -> float:
        pass

    @abstractmethod
    def get_status(self) -> bool:
        pass

    @abstractmethod
    def set_status(self, status: bool) -> None:
        pass
