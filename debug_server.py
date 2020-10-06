import uvicorn

import server


if __name__ == "__main__":
    uvicorn.run(server,
                host="0.0.0.0",
                port=8000,
                http="h11",
                ws="websockets",
                log_level="trace",
                use_colors=False,
                debug=True)
