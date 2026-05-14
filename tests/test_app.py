import pytest

from sqlalchemy import select
from app.database import PredictionModel

input_invalid_cases = [
    {"exercise": "super"},
    {"smoking": "maybe"},
    {"age": "не число"},
    {"profession": "Astronaut"},
    {"age": None},
]

base_input = {
    "age": 34,
    "weight": 80,
    "height": 180,
    "exercise": "medium",
    "sleep": 8,
    "sugar_intake": "low",
    "smoking": "no",
    "alcohol": "no",
    "married": "yes",
    "profession": "teacher",
    "bmi": 24.69,
}


@pytest.mark.asyncio
@pytest.mark.parametrize("override", input_invalid_cases)
async def test_validation_errors(client, override):
    response = await client.post("/predict", json={**base_input, **override})
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_prediction_is_deterministic(client):
    response1 = await client.post("/predict", json=base_input)
    response2 = await client.post("/predict", json=base_input)

    assert response1.status_code == response2.status_code == 200

    assert response1.json()["proba"] == response2.json()["proba"]


@pytest.mark.asyncio
async def test_prediction_saved_to_db(client, db):
    response = await client.post("/predict", json=base_input)
    assert response.status_code == 200

    data = response.json()

    results = await db.execute(select(PredictionModel))
    records = results.scalars().all()
    assert len(records) == 1

    record: PredictionModel = records[0]
    assert record.age == base_input["age"]
    assert record.profession == base_input["profession"]
    assert record.predict == data["class"]
    assert record.predict_proba == data["proba"]
