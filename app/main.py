import joblib
import logging
from typing import Literal, TypeAlias

from fastapi import FastAPI
from pydantic import BaseModel, field_validator
import pandas as pd
import numpy as np

from app.database import PredictionModel
from app.deps import SessionDep
from app.lifespan import lifespan

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BinLiteral: TypeAlias = Literal["yes", "no"]


_EXERCISE_MAP = {"none": 0, "low": 1, "medium": 2, "high": 3}
_SUGAR_INTAKE_MAP = {k: v - 1 for k, v in _EXERCISE_MAP.items() if k != "none"}
_BIN_COLS = ["smoking", "alcohol", "married"]


try:
    with open("models/model.pkl", "rb") as f:
        model = joblib.load(f)
    logger.info("Model loaded successfully")

except Exception as e:
    logger.error(f"Error loading model: {e}")

with open("models/scaler.joblib", "rb") as file:
    scaler = joblib.load(file)

with open("models/encoder.joblib", "rb") as file:
    encoder = joblib.load(file)
known_professions = encoder.categories_[0].tolist()


def prepare_features(df: pd.DataFrame) -> np.ndarray:
    df.drop("height", axis=1, inplace=True)

    df["exercise"] = df["exercise"].map(_EXERCISE_MAP).astype("int8")
    df["sugar_intake"] = df["sugar_intake"].map(_SUGAR_INTAKE_MAP).astype("int8")

    df[_BIN_COLS] = df[_BIN_COLS].replace({"yes": 1, "no": 0}).astype("int8")

    encoded_professions = encoder.transform(df[["profession"]])
    encoded_df = pd.DataFrame(
        encoded_professions,
        columns=encoder.get_feature_names_out(["profession"]),
        dtype="int8",
    )
    df = pd.concat([df, encoded_df], axis=1)
    df.drop("profession", axis=1, inplace=True)
    print(df.columns)

    return scaler.transform(df.values)


app = FastAPI(title="Health Risk", lifespan=lifespan)


class HealthFeatures(BaseModel):
    age: int
    weight: int
    height: int
    exercise: Literal["none", "low", "medium", "high"]
    sleep: float
    sugar_intake: Literal["low", "medium", "high"]
    smoking: BinLiteral
    alcohol: BinLiteral
    married: BinLiteral
    profession: str
    bmi: float

    @field_validator("profession")
    @classmethod
    def validate_profession(cls, v: str) -> str:
        if v not in known_professions:
            raise ValueError(
                f"Unknown profession '{v}'. " f"Valid values: {known_professions}"
            )
        return v


@app.post("/predict")
async def predict(features: HealthFeatures, session: SessionDep):
    input_data = pd.DataFrame([features.model_dump()])
    prepared_features = prepare_features(input_data)

    predicted_class = int(model.predict(prepared_features)[0])
    predicted_proba = float(model.predict_proba(prepared_features)[0, 1])


    session.add(
        PredictionModel(
            **features.model_dump(),
            predict=predicted_class,
            predict_proba=predicted_proba,
        )
    )
    await session.commit()

    return {"predicted_class": predicted_class}
