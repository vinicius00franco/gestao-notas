from abc import ABC, abstractmethod
from typing import Any, List
import logging

logger = logging.getLogger(__name__)


class Observer(ABC):
    @abstractmethod
    def update(self, subject: Any, event_type: str, **kwargs):
        """Called when the subject emits an event.

        event_type: a string identifying the event (e.g. 'lancamento_created')
        kwargs: additional context (models, data)
        """
        pass


class Subject:
    def __init__(self):
        self._observers: List[Observer] = []

    def attach(self, observer: Observer):
        if observer not in self._observers:
            self._observers.append(observer)

    def detach(self, observer: Observer):
        if observer in self._observers:
            self._observers.remove(observer)

    def notify(self, event_type: str, **kwargs):
        for observer in list(self._observers):
            try:
                observer.update(self, event_type, **kwargs)
            except Exception as e:
                logger.exception("Observer error: %s", e)
