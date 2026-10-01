from backend.services.mlflow_service import (
    start_mlflow_run,
    log_parameter,
    log_metric,
    end_mlflow_run,
)


run = start_mlflow_run(
    experiment_name="AtlasML_Test",
    run_name="test_run",
)

log_parameter("test_parameter", "hello")

log_metric("test_accuracy", 0.95)

end_mlflow_run()

print("MLflow test completed successfully.")