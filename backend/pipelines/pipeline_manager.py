from backend.models.pipeline_state import PipelineState
from backend.agents.dataset_agent import DatasetAgent


class PipelineManager:

    def __init__(self):
        self.dataset_agent = DatasetAgent()

    def run_pipeline(self, state: PipelineState):

        state = self.dataset_agent.run(state)

        return state