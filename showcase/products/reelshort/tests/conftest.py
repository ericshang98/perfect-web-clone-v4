from __future__ import annotations

import os
import shutil
import socket
import subprocess
import time
import urllib.request
from dataclasses import dataclass
from pathlib import Path

import pytest


@dataclass(frozen=True)
class PreviewServer:
    url: str
    project_dir: Path
    dist_dir: Path


def _reserve_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def _copy_tracked_product(product_dir: Path, destination: Path) -> None:
    repository = product_dir.parents[2]
    prefix = product_dir.relative_to(repository).as_posix() + "/"
    tracked = subprocess.run(
        ["git", "ls-files", "-z", "--", prefix],
        cwd=repository,
        check=True,
        capture_output=True,
    ).stdout.split(b"\0")
    for raw_path in tracked:
        if not raw_path:
            continue
        relative_to_repo = Path(os.fsdecode(raw_path))
        relative_to_product = relative_to_repo.relative_to(product_dir.relative_to(repository))
        if relative_to_product.parts[0] in {"dist", "node_modules", "shots", "tests"}:
            continue
        source = repository / relative_to_repo
        target = destination / relative_to_product
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)


def _wait_until_ready(url: str, process: subprocess.Popen[str]) -> None:
    deadline = time.monotonic() + 30
    last_error: Exception | None = None
    while time.monotonic() < deadline:
        if process.poll() is not None:
            stdout, stderr = process.communicate()
            raise RuntimeError(
                f"preview exited before becoming ready ({process.returncode})\n"
                f"stdout:\n{stdout}\nstderr:\n{stderr}"
            )
        try:
            with urllib.request.urlopen(url, timeout=1) as response:
                if response.status == 200:
                    return
        except Exception as exc:  # noqa: BLE001 - readiness polling.
            last_error = exc
        time.sleep(0.1)
    raise RuntimeError(f"preview did not become ready: {last_error}")


@pytest.fixture(scope="session")
def reelshort_preview(tmp_path_factory: pytest.TempPathFactory) -> PreviewServer:
    """Build tracked sources and own an ephemeral strict Vite preview."""

    product_dir = Path(__file__).resolve().parents[1]
    project_dir = tmp_path_factory.mktemp("reelshort-preview")
    _copy_tracked_product(product_dir, project_dir)
    dist_dir = project_dir / "dist"
    assert not dist_dir.exists(), "fixture must not copy a stale dist directory"
    subprocess.run(
        ["npm", "ci", "--ignore-scripts"],
        cwd=project_dir,
        check=True,
        capture_output=True,
        text=True,
    )
    subprocess.run(
        ["npm", "run", "build"],
        cwd=project_dir,
        check=True,
        capture_output=True,
        text=True,
    )
    assert (dist_dir / "index.html").is_file(), "fresh build produced no dist/index.html"

    process: subprocess.Popen[str] | None = None
    url = ""
    last_start_error: Exception | None = None
    for _attempt in range(5):
        port = _reserve_port()
        url = f"http://127.0.0.1:{port}/"
        process = subprocess.Popen(
            [
                "npm",
                "run",
                "preview",
                "--",
                "--host",
                "127.0.0.1",
                "--port",
                str(port),
                "--strictPort",
            ],
            cwd=project_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            start_new_session=True,
        )
        try:
            _wait_until_ready(url, process)
            break
        except RuntimeError as exc:
            last_start_error = exc
            if process.poll() is None:
                os.killpg(process.pid, 15)
                process.wait(timeout=5)
    else:
        raise RuntimeError(
            f"preview could not claim an ephemeral port after 5 attempts: "
            f"{last_start_error}"
        )

    assert process is not None
    try:
        yield PreviewServer(url=url, project_dir=project_dir, dist_dir=dist_dir)
    finally:
        if process.poll() is None:
            os.killpg(process.pid, 15)
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                os.killpg(process.pid, 9)
                process.wait(timeout=5)
