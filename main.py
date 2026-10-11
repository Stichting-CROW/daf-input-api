from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

import mevent
import webhook_pusher
from db import create_pool, get_db
from exceptions import InvalidUsage
from models import EventIn

output = webhook_pusher.WebHookPusher()


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.pool = create_pool()
    output.start()
    try:
        yield
    finally:
        output.stop()
        app.state.pool.close()


app = FastAPI(title="DAF Input API", version="0.2.0", lifespan=lifespan)


@app.exception_handler(InvalidUsage)
async def handle_invalid_usage(request: Request, error: InvalidUsage):
    return JSONResponse(status_code=error.status_code, content=error.to_dict())


@app.exception_handler(RequestValidationError)
async def handle_validation_error(request: Request, error: RequestValidationError):
    messages = "; ".join(
        ".".join(str(part) for part in item["loc"]) + ": " + item["msg"]
        for item in error.errors()
    )
    return JSONResponse(
        status_code=422,
        content={"message": "Incorrect JSON input. [" + messages + "]"},
    )


@app.post("/event")
def input_event(data: EventIn, conn=Depends(get_db)):
    msg = mevent.Event.insert(conn, data)
    if msg:
        output.enqueue(msg)
    return {"status": "created"}
