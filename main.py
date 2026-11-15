from fastapi import FastAPI
from pydantic import BaseModel
import predict


app = FastAPI()


class PredictionRequest(BaseModel):
    median_income: float
    housing_median_age: float
    total_rooms: float

@app.post("/predict")
def get_predict(data: PredictionRequest):
    return {"prediction": predict.make_prediction(data.median_income,data.housing_median_age,data.total_rooms)}