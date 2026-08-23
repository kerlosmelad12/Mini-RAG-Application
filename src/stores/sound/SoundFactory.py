from .SoundInteface import SoundProviderInterface
from .SoundEnums import SoundProviderEnums
from .providers.WhisperProvider import WhisperProvider  

class SoundProviderFactory:


    def __init__(self, config):
        self.config = config

    def create(self, provider: str) -> SoundProviderInterface:

        if provider == SoundProviderEnums.WHISPER.value:
            return WhisperProvider(
                model_size=self.config.WHISPER_MODEL_SIZE,
                device=self.config.WHISPER_DEVICE,
                compute_type=self.config.WHISPER_COMPUTE_TYPE,
                language=None,
            )

        return None