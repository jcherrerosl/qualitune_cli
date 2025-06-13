.PHONY: audit feed rate run
 
install:
	@echo "Installing dependencies..."
	@pip install -r requirements.txt
	@echo "Dependencies installed successfully."

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
	@./venv/bin/streamlit run app.py
	@echo "Qualitune is running. Open your browser to view the app."
	

venv:
	@echo "Creating virtual environment..."
	@python3.9 -m venv venv
	@echo "Activating virtual environment..."
	@source venv/bin/activate

commit:
	@git add .
	@./commit.sh
	@INPUT_VAR=$$(cat input.txt) && git commit -m "$(shell date +"%Y-%m-%d %H:%M:%S"):  $$INPUT_VAR" && rm -f input.txt
	@git push