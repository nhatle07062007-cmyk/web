from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

BASE_DIR = Path(__file__).resolve().parent

app = FastAPI(title="Phân tích biến động giá")


@app.get("/")
async def home():
	return FileResponse(BASE_DIR / "index.html")


@app.get("/health")
async def health():
	return {"status": "ok"}


app.mount(
	"/phan_tich_gia",
	StaticFiles(directory=BASE_DIR / "phan_tich_gia"),
	name="phan_tich_gia",
)


@app.get("/style.css")
async def style():
	return FileResponse(BASE_DIR / "style.css", media_type="text/css")


@app.get("/scripts.js")
async def scripts():
	return FileResponse(BASE_DIR / "scripts.js", media_type="application/javascript")


@app.get("/dothi.mp4")
async def video():
	return FileResponse(BASE_DIR / "dothi.mp4", media_type="video/mp4")