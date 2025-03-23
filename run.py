"""Application runner."""

import uvicorn

if __name__ == "__main__":
    uvicorn.run("webapp.application:app", host="0.0.0.0", port=8000, reload=True) 