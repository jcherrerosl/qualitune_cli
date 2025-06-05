.PHONY: audit feed rate run

audit:
	@echo "Separating good songs and outliers..."
	@python detect_and_export_outliers.py
	@echo "Process completed. Dataset ready for next batch."

feed:
	@python generate_csv_from_playlist.py
	@echo "Generating CSV from the playlist..."
	@echo "Extracting and analyzing songs from songs.csv..."
	@python extract_and_analyze.py
	@echo "Songs processed and added to reference_dataset.csv."

rate:
	@python rating_engine.py

run:
	@echo "Launching Qualitune..."
	@streamlit run app.py

venv:
	@echo "Creating virtual environment..."
	@python3.9 -m venv venv
	@echo "Activating virtual environment..."
	@source venv/bin/activate