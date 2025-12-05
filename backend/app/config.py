import os
from pathlib import Path
from typing import List


def _get_env_list(name: str, default: str = "") -> List[str]:
    """
    Read a comma-separated env var and convert to a list.
    """
    value = os.getenv(name, default)
    return [v.strip() for v in value.split(",") if v.strip()]


class Settings:
    # Database settings
    DB_USERNAME: str = os.getenv("DB_USERNAME", "dev_user")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "dev_password")
    DB_HOST: str = os.getenv("DB_HOST", "localhost")
    DB_PORT: int = int(os.getenv("DB_PORT", "5432"))

    # EDA / feature names
    EDA_FEATURE_NAMES: List[str] = _get_env_list(
        "EDA_FEATURE_NAMES", "age,income,years_with_company"
    )

    # Model hyperparameters
    MODEL_LEARNING_RATE: float = float(os.getenv("MODEL_LEARNING_RATE", "0.001"))
    MODEL_MAX_DEPTH: int = int(os.getenv("MODEL_MAX_DEPTH", "5"))
    MODEL_N_ESTIMATORS: int = int(os.getenv("MODEL_N_ESTIMATORS", "100"))

    # Experiment metadata
    MODEL_EXPECTED_ACCURACY: float = float(os.getenv("MODEL_EXPECTED_ACCURACY", "0.80"))
    MODEL_NUM_EPOCHS: int = int(os.getenv("MODEL_NUM_EPOCHS", "10"))
    EXPERIMENT_NAME: str = os.getenv("EXPERIMENT_NAME", "baseline_experiment")
    EXPERIMENT_VERSION: str = os.getenv("EXPERIMENT_VERSION", "v1")

    # Project root (useful later if needed)
    BASE_DIR: Path = Path(__file__).resolve().parent.parent


settings = Settings()
