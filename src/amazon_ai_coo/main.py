from fastapi import FastAPI

from amazon_ai_coo import __version__
from amazon_ai_coo.api.routes import router

app = FastAPI(
    title="Amazon AI COO",
    version=__version__,
    description="Unified seller state, diagnosis, guarded recommendation and execution API.",
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "version": __version__}


app.include_router(router)
