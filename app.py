
import os
import logging
from typing import Dict, Any

import requests
import streamlit as st

# --- Конфигурация ---
API_URL: str = os.getenv("API_URL", "http://localhost:8000/predict")
REQUEST_TIMEOUT: int = 5

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def send_prediction_request(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Отправляет POST-запрос на сервер для получения прогноза цены дома.
    """
    try:
        response = requests.post(API_URL, json=payload, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.ConnectionError:
        logger.error("Не удалось подключиться к серверу.")
        raise
    except requests.exceptions.Timeout:
        logger.error("Превышено время ожидания ответа от сервера.")
        raise
    except requests.exceptions.HTTPError as e:
        logger.error(f"HTTP ошибка: {e.response.status_code} - {e.response.text}")
        raise
    except Exception as e:
        logger.error(f"Непредвиденная ошибка: {e}")
        raise


def main() -> None:
    """Точка входа в приложение Streamlit."""
    
    # Настройки страницы (вкладка браузера и ширина контента)
    st.set_page_config(page_title="Прогноз стоимости жилья", layout="centered")
    
    st.title("Оценка стоимости дома в Калифорнии")
    st.caption("Заполните параметры недвижимости для получения прогноза.")
    
    # Оборачиваем форму в контейнер с рамкой для аккуратного вида
    with st.container(border=True):
        with st.form("prediction_form"):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                median_income = st.number_input(
                    "Медианный доход", 
                    min_value=0.0, 
                    max_value=15.0, 
                    value=3.5, 
                    step=0.1, 
                    format="%.2f",
                    help="В десятках тысяч долларов (например, 3.5 = $35,000)"
                )
            with col2:
                housing_median_age = st.number_input(
                    "Возраст жилья (лет)", 
                    min_value=1.0, 
                    max_value=100.0, 
                    value=25.0, 
                    step=1.0, 
                    format="%.1f",
                    help="Средний возраст домов в квартале"
                )
            with col3:
                total_rooms = st.number_input(
                    "Всего комнат", 
                    min_value=1.0, 
                    max_value=50000.0, 
                    value=1500.0, 
                    step=10.0, 
                    format="%.1f",
                    help="Общее число комнат в квартале"
                )
                
            submit_button = st.form_submit_button("Рассчитать", type="primary")

    # Обработка отправки формы
    if submit_button:
        payload = {
            "median_income": float(median_income),
            "housing_median_age": float(housing_median_age),
            "total_rooms": float(total_rooms)
        }
        
        with st.spinner("Ожидание ответа от сервера..."):
            try:
                result = send_prediction_request(payload)
                st.success("Прогноз успешно получен.")
                
                prediction_value = result.get("prediction", "Неизвестный формат")
                
                # Проверка, что пришло число, чтобы не упало форматирование
                if isinstance(prediction_value, (int, float)):
                    st.metric(label="Предсказанная стоимость", value=f"${prediction_value:,.2f}")
                else:
                    st.warning(f"Неожиданный формат ответа: {result}")
                
            except requests.exceptions.ConnectionError:
                st.error("Сервер недоступен. Проверьте соединение с бэкендом.")
            except requests.exceptions.Timeout:
                st.error("Превышено время ожидания. Сервер не отвечает.")
            except requests.exceptions.HTTPError as e:
                st.error(f"Ошибка сервера: {e.response.status_code}")
                st.code(e.response.text, language="json")
            except Exception:
                st.error("Не удалось обработать запрос. Повторите попытку позже.")


if __name__ == "__main__":
    main()