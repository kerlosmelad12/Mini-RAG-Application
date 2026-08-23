from abc import ABC, abstractmethod
from typing import Optional, Dict


class SoundProviderInterface(ABC):


    @abstractmethod
    def transcribe(self, sound_path: str) -> Optional[Dict]:

        pass