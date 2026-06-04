from faster_whisper import WhisperModel

from app.models.schemas import Segment, TranscriptionResult, Word


class WhisperService:
    def __init__(self):
        self._model = None
        self._loaded_model_name = None

    def _get_model(self, model_name: str) -> WhisperModel:
        if model_name == self._loaded_model_name:
            return self._model
        self._model = WhisperModel(
            model_name,
            device="cpu",
            compute_type="int8",
            download_root="data/whisper_models",
        )
        self._loaded_model_name = model_name
        return self._model

    def transcribe(
        self,
        audio_path: str,
        model: str = "base",
        language: str = "auto",
        word_timestamps: bool = True,
    ) -> TranscriptionResult:
        current_model = self._get_model(model_name=model)
        segments, info = current_model.transcribe(
            audio_path,
            language=None if language == "auto" else language,
            word_timestamps=word_timestamps,
        )

        built_segments = []
        for segment in segments:
            words = [
                Word(
                    start=w.start,
                    end=w.end,
                    word=w.word,
                    probability=w.probability,
                )
                for w in (segment.words or [])
            ]
            built_segments.append(
                Segment(
                    start=segment.start,
                    end=segment.end,
                    text=segment.text,
                    words=words,
                )
            )

        return TranscriptionResult(
            language=info.language,
            language_probability=info.language_probability,
            duration=info.duration,
            segments=built_segments,
        )


whisper_service = WhisperService()
