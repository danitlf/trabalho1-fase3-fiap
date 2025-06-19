from pydantic import BaseModel
from datetime import datetime
from typing import List

weather_codes_chuvosos = [
    51, 53, 55,        # Chuvisco (leve, moderado, intenso)
    56, 57,            # Chuvisco congelante
    61, 63, 65,        # Chuva (fraca, moderada, forte)
    66, 67,            # Chuva congelante
    80, 81, 82,        # Pancadas de chuva (leves, moderadas, fortes)
    95, 96, 99         # Tempestade (com ou sem granizo)
]

class SensorBase(BaseModel):
    id: int
    nome: str

class LeituraBase(BaseModel):
    valor: float

class LeituraCreate(LeituraBase):
    sensor_id: int

class PredictCreate(BaseModel):
    sensor_humidity: float
    sensor_k: float
    sensor_p: float
    sensor_ph: float
    sensor_temperature: float

class PredictResponse(BaseModel):
    pred: float

class LeituraRead(LeituraBase):
    id: int
    timestamp: datetime
    sensor: SensorBase

    class Config:
        orm_mode = True

class SensorRead(SensorBase):
    leituras: List[LeituraRead] = []

    class Config:
        orm_mode = True

class SensorCreate(BaseModel):
    nome: str

class IsRainning(BaseModel):
    is_raining: bool

    @classmethod
    def from_api(cls, dados):
        return cls(
            is_raining=dados["current_weather"]["weathercode"] in weather_codes_chuvosos
        )

class PredictsResponse(BaseModel):
    pass