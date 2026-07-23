from fastapi import FastAPI

app = FastAPI(title="Forge AI Engineering Platform")

@app.get("/")
def read_root():
    return {"status": "Forge AI Engine Running"}
