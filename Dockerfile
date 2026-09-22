# Optional reproducible runner for the imagery/DEM pipeline modes.
# Scoring, validation, export, tests, and the static demo need no container
# (stdlib only). This image adds numpy/Pillow/rasterio/pyproj for dem/spread.
FROM python:3.11-slim
WORKDIR /work
COPY mineral_pipeline.py scripts/ ./
RUN pip install --no-cache-dir numpy pillow rasterio pyproj
CMD ["python3", "mineral_pipeline.py", "--help"]
