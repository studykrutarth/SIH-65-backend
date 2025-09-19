from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
import xarray as xr
import pandas as pd

NC_PATH = "RF25_ind2023_rfp25.nc"
VAR = "RAINFALL"   # use correct variable name

# Open dataset with decode_times
ds = xr.open_dataset(NC_PATH, decode_times=True)

app = FastAPI(title="Rainfall API")

# Allow CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_monthly_rain(lat: float, lon: float):
    """Return monthly rainfall (mm) for nearest gridpoint"""
    series = ds[VAR].sel(LATITUDE=lat, LONGITUDE=lon, method="nearest").to_series()
    # Index is already datetime
    monthly = series.resample("M").sum()
    return [{"month": idx.strftime("%b"), "rain_mm": float(v)} for idx, v in monthly.items()]

@app.get("/rain/point")
def rain_point(lat: float = Query(...), lon: float = Query(...)):
    return {"lat": lat, "lon": lon, "monthly": get_monthly_rain(lat, lon)}

@app.get("/rain/annual")
def rain_annual(lat: float = Query(...), lon: float = Query(...)):
    monthly = get_monthly_rain(lat, lon)
    annual_total = sum(m["rain_mm"] for m in monthly)
    return {"lat": lat, "lon": lon, "annual_rain_mm": annual_total}
