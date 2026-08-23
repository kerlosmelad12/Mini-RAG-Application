import logging
from typing import Optional, Dict

from faster_whisper import WhisperModel

from ..SoundInteface import SoundProviderInterface
from ..SoundEnums import WhisperDeviceEnums, WhisperComputeTypeEnums


class WhisperProvider(SoundProviderInterface):

    def __init__(
        self,
        model_size: str,
        device: str = WhisperDeviceEnums.CPU.value,
        compute_type: str = WhisperComputeTypeEnums.INT8.value,
        language: Optional[str] = None,
    ):
        self.model_size = model_size
        self.device = device
        self.compute_type = compute_type
     
        self.language = language

        self.model = WhisperModel(
            self.model_size,
            device=self.device,
            compute_type=self.compute_type,
        )

    def transcribe(self, sound_path: str) -> Optional[Dict]:
        try:
            segments, info = self.model.transcribe(
                sound_path,
                language=self.language,
                task="transcribe",
            )

            full_text = " ".join([segment.text for segment in segments])

            return {
                "text": full_text.strip(),
                "detected_language": info.language,
                "confidence": info.language_probability,
            }

        except Exception as e:
            logging.error(f"[WhisperProvider] Transcription failed for {sound_path}: {e}")
            return None