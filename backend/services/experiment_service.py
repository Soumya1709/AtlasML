from uuid import uuid4
from datetime import datetime
from backend.models.experiment import Experiment

experiments = {}


def create_experiment(dataset_name, dataset_path):

    experiment = Experiment(
        experiment_id=str(uuid4()),
        dataset_name=dataset_name,
        dataset_path=dataset_path,
        status="uploaded",
        created_at=datetime.now(),
        updated_at=datetime.now()
    )

    experiments[experiment.experiment_id] = experiment

    return experiment


def get_experiment(experiment_id):

    return experiments.get(experiment_id)


def get_all_experiments():

    return list(experiments.values())