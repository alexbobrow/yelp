from fastapi import FastAPI

from api.v1.company import company_router
from config.containers import Container


app = FastAPI()
container = Container()
app.container = container
app.include_router(company_router, prefix="/api")
