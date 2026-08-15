from backend.agents.dataset_agent import DatasetAgent
from backend.agents.cleaning_agent import CleaningAgent


AGENT_REGISTRY = {
    "DatasetAgent": DatasetAgent,
    "CleaningAgent": CleaningAgent,
}