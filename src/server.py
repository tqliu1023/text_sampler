import threading
import random
from fastapi import FastAPI, UploadFile, File, HTTPException
from typing import List

# FastAPI app instance
app = FastAPI()

# Thread-safe global cache for storing lines
cache_lock = threading.Lock()
global_cache = []

# Endpoint to clear the cache (for testing)
@app.post("/reset/")
def reset():
    """Test-only endpoint to clear the cache."""
    with cache_lock:
        global_cache.clear()
    return {"status": "cache cleared"}

# Endpoint to load lines from a text file into the cache
@app.post("/load/")
def load(file: UploadFile = File(...)):
    lines = file.file.read().decode("utf-8").splitlines()
    # Optionally filter out empty lines
    lines = [line for line in lines]
    with cache_lock:
        global_cache.extend(lines)
    return {"lines_read": len(lines)}

# Endpoint to sample N random lines from the cache
@app.post("/sample/")
def sample(n: int):
    with cache_lock:
        if not isinstance(n, int) or n <= 0:
            raise HTTPException(status_code=400, detail="Sample size must be positive integer.")
        if n > len(global_cache):
            raise HTTPException(status_code=400, detail="Not enough lines in cache.")
        if len(global_cache) == 0:
            raise HTTPException(status_code=400, detail="Cache is empty.")
        sampled = random.sample(global_cache, n)
        for line in sampled:
            global_cache.remove(line)
    return {"sampled_lines": sampled}
