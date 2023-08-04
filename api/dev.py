import logging

import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "api.app:app",
        host="0.0.0.0",
        port=5000,
        reload=True,
        log_level=logging.DEBUG,
        use_colors=True,
    )
