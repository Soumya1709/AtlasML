from backend.agents.dataset_agent import DatasetAgent
from backend.agents.cleaning_agent import CleaningAgent
from backend.agents.eda_agent import EDAAgent
from backend.agents.feature_agent import FeatureAgent
from backend.agents.model_selection_agent import ModelSelectionAgent
from backend.agents.training_agent import TrainingAgent
from backend.agents.deployment_agent import DeploymentAgent
from backend.agents.hyperparameter_tuning_agent import (
    HyperparameterTuningAgent,
)
from backend.agents.evaluation_agent import EvaluationAgent
from backend.agents.shap_agent import SHAPAgent
from backend.agents.report_agent import ReportAgent


AGENT_REGISTRY = {
    "DatasetAgent": DatasetAgent,
    "CleaningAgent": CleaningAgent,
    "EDAAgent": EDAAgent,
    "FeatureAgent": FeatureAgent,
    "ModelSelectionAgent": ModelSelectionAgent,
    "TrainingAgent": TrainingAgent,
    "HyperparameterTuningAgent": HyperparameterTuningAgent,
    "EvaluationAgent": EvaluationAgent,
    "SHAPAgent": SHAPAgent,
    "ReportAgent": ReportAgent,
    "DeploymentAgent": DeploymentAgent,
}