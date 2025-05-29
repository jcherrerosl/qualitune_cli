.PHONY: audit feed rate

# 🔍 Separa canciones buenas y outliers, y limpia el CSV de entrada
audit:
	@echo "🔍 Separando canciones limpias y outliers..."
	@python detect_and_export_outliers.py
	@echo "✅ Proceso completado. Dataset listo para siguiente batch."

# 🎧 Extrae MP3s y analiza canciones desde songs.csv
feed:
	python generate_csv_from_playlist.py
	@echo "🎧 Generando CSV desde la playlist..."
	@echo "🎧 Extrayendo y analizando canciones desde songs.csv..."
	@python extract_and_analyze.py
	@echo "✅ Canciones procesadas y añadidas a reference_dataset.csv."

# 🧠 Analiza una canción individual y la registra en rated_songs.csv
rate:
	@python rating_engine.py
