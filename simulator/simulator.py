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


while True:
    sleep(1)
    print("Simulando leitura")

    #resgatar sensores
    response = requests.get("http://localhost:8000/sensores/")
    sensores = response.json()

    for sensor in sensores:
        print(f"Sensor {sensor['nome']} - ID: {sensor['id']}")

        #simular leitura
        valor = sensor_simulator(sensor['nome'])
        response = requests.post(f"http://localhost:8000/leituras/", json={"valor": valor, "sensor_id": sensor['id']})
        print(response.json())

    