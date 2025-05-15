from fastapi import FastAPI, Depends, HTTPException
from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.models import Base, Sensor, Leitura
from src.schemas import *
import streamlit as st


import requests

DATABASE_URL = "sqlite:///./teste.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)

Base.metadata.create_all(bind=engine)

app = FastAPI()

# Dependência para injetar sessão do banco
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/sensores/", response_model=List[SensorRead])
def listar_sensores(db: Session = Depends(get_db)):
    return db.query(Sensor).all()

@app.post("/sensores/", response_model=SensorRead)
def criar_sensor(sensor: SensorCreate, db: Session = Depends(get_db)):
    db_sensor = Sensor(**sensor.model_dump())
    db.add(db_sensor)
    db.commit()
    db.refresh(db_sensor)
    return db_sensor

@app.delete("/sensores/{sensor_id}")
def deletar_sensor(sensor_id: int, db: Session = Depends(get_db)):
    db_sensor = db.query(Sensor).filter(Sensor.id == sensor_id).first()
    if not db_sensor:
        raise HTTPException(status_code=404, detail="Sensor não encontrado")
    db.delete(db_sensor)
    db.commit()
    return {"message": "Sensor deletado com sucesso"}

@app.put("/sensores/{sensor_id}", response_model=SensorRead)
def atualizar_sensor(sensor_id: int, sensor: SensorCreate, db: Session = Depends(get_db)):
    db_sensor = db.query(Sensor).filter(Sensor.id == sensor_id).first()
    if not db_sensor:
        raise HTTPException(status_code=404, detail="Sensor não encontrado")
    db_sensor.nome = sensor.nome
    db.commit()
    db.refresh(db_sensor)
    return db_sensor

@app.post("/leituras/", response_model=LeituraRead)
def criar_leitura(leitura: LeituraCreate, db: Session = Depends(get_db)):
    db_leitura = Leitura(**leitura.model_dump())
    db.add(db_leitura)
    db.commit()
    db.refresh(db_leitura)
    return db_leitura

@app.get("/leituras/{sensor_id}", response_model=List[LeituraRead])
def listar_leituras(sensor_id: int, db: Session = Depends(get_db)):
    return db.query(Leitura).filter(Leitura.sensor_id == sensor_id).all()

@app.get("/sensores/{sensor_id}", response_model=SensorRead)
def buscar_sensor(sensor_id: int, db: Session = Depends(get_db)):
    return db.query(Sensor).filter(Sensor.id == sensor_id).first()

@app.get("/israinning", response_model=IsRainning)
def previsao():
    response = requests.get("https://api.open-meteo.com/v1/forecast?latitude=-23.08639&longitude=-46.95056&current_weather=true")
    data = response.json()
    return IsRainning.from_api(data)

@st.cache_data(ttl=10)          # auto-refresh a cada 10 s
def load_data(n_linhas=5000):
    df = pd.read_sql(
        "SELECT * FROM leituras ORDER BY ts DESC LIMIT ?",
        get_db(), params=(n_linhas,)
    )
    return df

