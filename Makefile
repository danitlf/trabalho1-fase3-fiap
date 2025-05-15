run_dashboard:
	streamlit run dashboard.py

run_api:
	uvicorn main:app --reload

run_simulador:
	python simulator/simulator.py

install_dependences:
	virtualenv my-env
	source my-env/bin/activate
	pip install -r requirements.txt