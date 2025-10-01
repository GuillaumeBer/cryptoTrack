import uvicorn
import sys
import asyncio

if __name__ == "__main__":
    # On Windows, the default asyncio event loop (ProactorEventLoop) can cause
    # a ConnectionResetError. Switching to the SelectorEventLoop, which is
    # the default on other platforms, resolves this issue.
    if sys.platform == "win32":
        print("Applying WindowsSelectorEventLoopPolicy to prevent ConnectionResetError.")
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    # We run the server programmatically to ensure the event loop policy is
    # applied before the server starts. The application is specified as a
    # string 'src.main:app' to allow Uvicorn to import it correctly.
    uvicorn.run("src.main:app", host="0.0.0.0", port=8000, reload=True)