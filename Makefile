run_dashboard:
	streamlit run dashboard.py

run_api:
	uvicorn main:app --reload

run_simulador:
	python simulator/simulator.py

	