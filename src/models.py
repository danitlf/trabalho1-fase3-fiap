from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime

Base = declarative_base()

class Sensor(Base):
    __tablename__ = 'sensores'

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False)

    leituras = relationship("Leitura", back_populates="sensor")


class Leitura(Base):
    __tablename__ = 'leituras'

    id = Column(Integer, primary_key=True, index=True)
    valor = Column(Float, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)

    sensor_id = Column(Integer, ForeignKey('sensores.id'))
    sensor = relationship("Sensor", back_populates="leituras")

class Predict(Base):
    __tablename__ = 'predicts'

    id = Column(Integer, primary_key=True, index=True)
    valor = Column(Integer, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)