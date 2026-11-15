import pandas as pd
from catboost import CatBoostRegressor

model = CatBoostRegressor()
model.load_model("model.cbm")

def make_prediction(median_income, housing_median_age, total_rooms):
    input_data = pd.DataFrame([{
        'median_income': median_income,
        'housing_median_age': housing_median_age,
        'total_rooms': total_rooms
    }])
    
    prediction = model.predict(input_data)[0]
    return float(prediction)

if __name__ == "__main__":
    test_price = make_prediction(8.3252, 41.0, 880.0)
    print(f"Тестовый прогноз: {test_price:.2f}")
