import queue
import tempfile
import os
import asyncio
import logging
from abc import ABC, abstractmethod
import edge_tts
from PyQt5.QtCore import QThread, pyqtSignal, QUrl
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from utils import logger
import config

# ---------------------------------------------------------------------------
# Voice Provider abstraction
# ---------------------------------------------------------------------------
class VoiceProvider(ABC):
    """Abstract base class for voice synthesis providers.
    Implementations must provide an async ``synthesize`` method that returns the
    absolute path to an audio file (MP3) containing the spoken text.
    """

    @abstractmethod
    async def synthesize(self, text: str) -> str:
        """Generate audio for *text* and return the path to the audio file.
        Implementations should raise an exception on failure.
        """
        raise NotImplementedError

    @property
    def name(self) -> str:
        return self.__class__.__name__


class EdgeTTSProvider(VoiceProvider):
    """Edge‑TTS implementation using the ``edge‑tts`` package.
    The default voice is taken from ``config.VOICE_DEFAULT``.
    """

    def __init__(self):
        self.voice = getattr(config, "VOICE_DEFAULT", "en-US-JennyNeural")
        logger.info(f"[VOICE] Edge‑TTS Provider initialized with voice {self.voice}")

    async def synthesize(self, text: str) -> str:
        communicate = edge_tts.Communicate(text, self.voice)
        fd, path = tempfile.mkstemp(suffix=".mp3", prefix="friday_tts_")
        os.close(fd)
        await communicate.save(path)
        return path


class DisabledProvider(VoiceProvider):
    """No‑op provider used when voice output is disabled.
    ``synthesize`` returns ``None`` and logs the request.
    """

    async def synthesize(self, text: str) -> str:
        logger.info("[VOICE] DisabledProvider received text – no audio will be generated.")
        return None


def get_voice_provider() -> VoiceProvider:
    """Factory that returns the provider indicated by ``config.VOICE_PROVIDER``.
    Supported values: ``"edge"`` (default), ``"disabled"``. Extend later for
    ElevenLabs etc.
    """
    provider_key = getattr(config, "VOICE_PROVIDER", "edge").lower()
    if provider_key == "edge":
        return EdgeTTSProvider()
    elif provider_key == "disabled":
        return DisabledProvider()
    else:
        logger.warning(f"[VOICE] Unknown provider '{provider_key}'. Falling back to DisabledProvider.")
        return DisabledProvider()

# ---------------------------------------------------------------------------
# TTSWorker – thread that manages the queue and playback
# ---------------------------------------------------------------------------
class TTSWorker(QThread):
    """Background thread that consumes text from a queue, uses the selected
    ``VoiceProvider`` to synthesize audio, and plays it via ``QMediaPlayer``.
    It preserves the original public API used throughout the codebase.
    """
    speaking_started = pyqtSignal(str)
    speaking_finished = pyqtSignal()
    queue_size_changed = pyqtSignal(int)
    error_occurred = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.queue = queue.Queue()
        self.running = True
        self.player = QMediaPlayer()
        self.player.mediaStatusChanged.connect(self._on_media_status_changed)
        self._current_file = None
        self.provider = get_voice_provider()
        self.is_running = False  # UI can query this flag

    # ---------------------------------------------------------------------
    # Public API
    # ---------------------------------------------------------------------
    def speak(self, text: str):
        """Enqueue *text* for synthesis.
        The method is thread‑safe because ``queue.Queue`` is thread‑safe.
        """
        if not text:
            return
        self.queue.put(text)
        logger.info("[VOICE] Received text")
        self.queue_size_changed.emit(self.queue.qsize())

    def stop(self):
        """Terminate the worker and clear pending items."""
        self.running = False
        self._clear_queue()
        self.wait()

    # ---------------------------------------------------------------------
    # Internal helpers
    # ---------------------------------------------------------------------
    def _clear_queue(self):
        while not self.queue.empty():
            try:
                self.queue.get_nowait()
                self.queue.task_done()
            except queue.Empty:
                break
        if self.player.state() == QMediaPlayer.PlayingState:
            self.player.stop()
        self._remove_temp_file()

    def _remove_temp_file(self):
        if self._current_file and os.path.exists(self._current_file):
            try:
                os.remove(self._current_file)
            except Exception as e:
                logger.error(f"[VOICE ERROR] Failed to delete temp audio file: {e}")
        self._current_file = None

    def _on_media_status_changed(self, status):
        from PyQt5.QtMultimedia import QMediaPlayer as MP
        if status == MP.EndOfMedia:
            logger.info("[VOICE] Playback completed")
            self.speaking_finished.emit()
            self._remove_temp_file()
            self._process_next()
        elif status == MP.LoadedMedia:
            logger.info("[VOICE] Playback started")
            self.player.play()

    def _process_next(self):
        if not self.running:
            return
        try:
            text = self.queue.get_nowait()
        except queue.Empty:
            return
        self.speaking_started.emit(text)
        logger.info(f"[VOICE] Generating audio for: {text}")
        # Run asynchronous synthesis inside the thread
        try:
            asyncio.run(self._synthesize_and_play(text))
        except Exception as e:
            logger.error(f"[VOICE ERROR] Async synthesis failed: {e}")
            self.error_occurred.emit(str(e))
            self.speaking_finished.emit()
        finally:
            self.queue.task_done()
            self.queue_size_changed.emit(self.queue.qsize())

    async def _synthesize_and_play(self, text: str):
        # Ask provider for a file path; may be None for DisabledProvider
        try:
            audio_path = await self.provider.synthesize(text)
            if not audio_path:
                # DisabledProvider – skip playback but still emit finished
                logger.info("[VOICE] Provider returned no audio; skipping playback.")
                self.speaking_finished.emit()
                return
            self._current_file = audio_path
            url = QUrl.fromLocalFile(audio_path)
            media = QMediaContent(url)
            self.player.setMedia(media)
        except Exception as e:
            logger.error(f"[VOICE ERROR] Synthesis failed: {e}")
            self.error_occurred.emit(str(e))
            self.speaking_finished.emit()
            self._remove_temp_file()

    def run(self):
        logger.info("TTSWorker thread started.")
        self.is_running = True
        while self.running:
            if not self.queue.empty():
                self._process_next()
            else:
                self.msleep(100)  # avoid busy‑wait
        self.is_running = False
        self._clear_queue()
        logger.info("TTSWorker thread stopped.")
