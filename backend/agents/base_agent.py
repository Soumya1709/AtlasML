from abc import ABC, abstractmethod

from backend.models.pipeline_state import PipelineState


class BaseAgent(ABC):

    @abstractmethod
    def run(self, state: PipelineState) -> PipelineState:
        pass