from fastapi import FastAPI

app = FastAPI(title='OlympSearch API')

@app.get('/', tags=['health'])
async def root():
    return {'status': 'ok'}
