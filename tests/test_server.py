import threading
import requests

# This is the server URL for API requests.
SERVER_URL = "http://127.0.0.1:8000"

# Helper function to clear the server cache before each test.
def reset_cache():
    requests.post(f"{SERVER_URL}/reset/")

# Test loading and sampling lines from a file.
def test_load_and_sample(tmp_path):
    reset_cache()
    # Create a test file
    test_file = tmp_path / "test.txt"
    lines = [f"line{i}" for i in range(10)]
    test_file.write_text("\n".join(lines))

    # Load file
    with open(test_file, "rb") as f:
        resp = requests.post(f"{SERVER_URL}/load/", files={"file": f})
        assert resp.status_code == 200
        assert resp.json()["lines_read"] == 10

    # Sample 5 lines
    resp = requests.post(f"{SERVER_URL}/sample/", params={"n": 5})
    assert resp.status_code == 200
    sampled = resp.json()["sampled_lines"]
    assert len(sampled) == 5
    # Sample remaining 5 lines
    resp = requests.post(f"{SERVER_URL}/sample/", params={"n": 5})
    assert resp.status_code == 200
    sampled = resp.json()["sampled_lines"]
    assert len(sampled) == 5
    # Try to sample more than available
    resp = requests.post(f"{SERVER_URL}/sample/", params={"n": 1})
    assert resp.status_code == 400

# Test loading an empty file.
def test_empty_file(tmp_path):
    reset_cache()
    test_file = tmp_path / "empty.txt"
    test_file.write_text("")
    with open(test_file, "rb") as f:
        resp = requests.post(f"{SERVER_URL}/load/", files={"file": f})
        assert resp.status_code == 200
        assert resp.json()["lines_read"] == 0

# Test concurrent sampling from the cache.
def test_concurrent_sampling(tmp_path):
    reset_cache()
    test_file = tmp_path / "concurrent.txt"
    lines = [f"line{i}" for i in range(100)]
    test_file.write_text("\n".join(lines))
    with open(test_file, "rb") as f:
        requests.post(f"{SERVER_URL}/load/", files={"file": f})

    results = []
    def sampler():
        resp = requests.post(f"{SERVER_URL}/sample/", params={"n": 10})
        if resp.status_code == 200:
            results.extend(resp.json()["sampled_lines"])

    threads = [threading.Thread(target=sampler) for _ in range(10)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    assert len(results) == 100

    # No lines left
    resp = requests.post(f"{SERVER_URL}/sample/", params={"n": 1})
    assert resp.status_code == 400

# Test duplicate lines in the cache.
def test_duplicate_lines(tmp_path):
    reset_cache()
    test_file = tmp_path / "dupes.txt"
    lines = ["a", "b", "a", "c", "b"]
    test_file.write_text("\n".join(lines))
    with open(test_file, "rb") as f:
        resp = requests.post(f"{SERVER_URL}/load/", files={"file": f})
        assert resp.status_code == 200
        assert resp.json()["lines_read"] == 5
    resp = requests.post(f"{SERVER_URL}/sample/", params={"n": 2})
    assert resp.status_code == 200
    sampled = resp.json()["sampled_lines"]
    assert len(sampled) == 2
    # Sample remaining lines
    resp = requests.post(f"{SERVER_URL}/sample/", params={"n": 3})
    assert resp.status_code == 200
    sampled = resp.json()["sampled_lines"]
    assert len(sampled) == 3
    # No lines left
    resp = requests.post(f"{SERVER_URL}/sample/", params={"n": 1})
    assert resp.status_code == 400

# Test sampling zero lines from the cache.
def test_sample_zero(tmp_path):
    reset_cache()
    test_file = tmp_path / "zero.txt"
    test_file.write_text("a\nb\nc")
    with open(test_file, "rb") as f:
        requests.post(f"{SERVER_URL}/load/", files={"file": f})
    resp = requests.post(f"{SERVER_URL}/sample/", params={"n": 0})
    assert resp.status_code == 400 or len(resp.json().get("sampled_lines", [])) == 0

# Test sampling negative number of lines from the cache.
def test_sample_negative(tmp_path):
    reset_cache()
    test_file = tmp_path / "neg.txt"
    test_file.write_text("a\nb\nc")
    with open(test_file, "rb") as f:
        requests.post(f"{SERVER_URL}/load/", files={"file": f})
    resp = requests.post(f"{SERVER_URL}/sample/", params={"n": -1})
    assert resp.status_code == 400

# Test loading a file with only whitespace/newlines.
def test_whitespace_file(tmp_path):
    reset_cache()
    test_file = tmp_path / "white.txt"
    test_file.write_text("\n\n\n")
    with open(test_file, "rb") as f:
        resp = requests.post(f"{SERVER_URL}/load/", files={"file": f})
        assert resp.status_code == 200
        assert resp.json()["lines_read"] == 3
    resp = requests.post(f"{SERVER_URL}/sample/", params={"n": 1})
    assert resp.status_code == 200
    sampled = resp.json()["sampled_lines"]
    # Accept any line, including empty string
    assert sampled[0] == "" or sampled[0] == "\n"

# Test loading and sampling from a very large file.
def test_large_file(tmp_path):
    reset_cache()
    test_file = tmp_path / "large.txt"
    lines = [str(i) for i in range(10000)]
    test_file.write_text("\n".join(lines))
    with open(test_file, "rb") as f:
        resp = requests.post(f"{SERVER_URL}/load/", files={"file": f})
        assert resp.status_code == 200
        assert resp.json()["lines_read"] == 10000
    resp = requests.post(f"{SERVER_URL}/sample/", params={"n": 10000})
    assert resp.status_code == 200
    sampled = resp.json()["sampled_lines"]
    assert len(sampled) == 10000
    resp = requests.post(f"{SERVER_URL}/sample/", params={"n": 1})
    assert resp.status_code == 400

# Test multiple clients loading files concurrently.
def test_multiple_clients_load(tmp_path):
    reset_cache()
    test_file1 = tmp_path / "client1.txt"
    test_file2 = tmp_path / "client2.txt"
    test_file1.write_text("a\nb\nc")
    test_file2.write_text("d\ne\nf")
    def loader(file):
        with open(file, "rb") as f:
            requests.post(f"{SERVER_URL}/load/", files={"file": f})
    threads = [threading.Thread(target=loader, args=(test_file1,)), threading.Thread(target=loader, args=(test_file2,))]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    resp = requests.post(f"{SERVER_URL}/sample/", params={"n": 6})
    assert resp.status_code == 200
    sampled = resp.json()["sampled_lines"]
    assert set(sampled) == set(["a", "b", "c", "d", "e", "f"])
