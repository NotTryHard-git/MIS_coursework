from fastapi import FastAPI



app = FastAPI(
    title="Warehouse Catalog"
)



# Базовый эндпоинт для проверки работы
@app.get("/")
async def root():
    return {
        "message": "Warehouse Catalog API",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
    



