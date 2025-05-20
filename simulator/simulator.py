from time import sleep
import random
import requests

def sensor_simulator(sensor_name):
    if "temperatura" in sensor_name.lower():
        return random.uniform(20, 40)
    elif "umidade" in sensor_name.lower():
        return random.uniform(40, 60)
    elif "ph" in sensor_name.lower():
        return random.uniform(5, 9)
    else:
        return random.uniform(0, 100)


# class Sensor(Base):
#     __tablename__ = 'sensores'

#     id = Column(Integer, primary_key=True, index=True)
#     nome = Column(String, nullable=False)
def create_sensors():
    sensor_temperature = requests.post("http://localhost:8000/sensores/", json={"nome": "sensor_temperature"})
    sensor_humidity = requests.post("http://localhost:8000/sensores/", json={"nome": "sensor_humidity"})
    sensor_ph = requests.post("http://localhost:8000/sensores/", json={"nome": "sensor_ph"})
    sensor_p = requests.post("http://localhost:8000/sensores/", json={"nome": "sensor_p"})
    sensor_k = requests.post("http://localhost:8000/sensores/", json={"nome": "sensor_k"})


    return [sensor_temperature.json(), sensor_humidity.json(), sensor_ph.json(), sensor_p.json(), sensor_k.json()]



while True:
    sleep(1)
    print("Simulando leitura")

    #resgatar sensores
    response = requests.get("http://localhost:8000/sensores/")
    sensores = response.json()

    if not sensores:
        sensores = create_sensors()

    for sensor in sensores:
        print(f"Sensor {sensor['nome']} - ID: {sensor['id']}")

        #simular leitura
        valor = sensor_simulator(sensor['nome'])
        response = requests.post(f"http://localhost:8000/leituras/", json={"valor": valor, "sensor_id": sensor['id']})
        print(response.json())

    