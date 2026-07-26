import asyncio
import json
import os
import socket
import sys
from pathlib import Path

from core.boxlite import sandbox_manager
from core.boxlite.models import CommandResult


def test_background_process_is_detached_and_logs_to_disk(tmp_path, monkeypatch):
    monkeypatch.setattr(sandbox_manager, "SANDBOX_BASE_DIR", str(tmp_path))

    async def exercise():
        sandbox = sandbox_manager.BoxLiteSandbox("detached")
        sandbox.work_dir.mkdir(parents=True)
        result = await sandbox.exec("printf 'ready\\n'; sleep 30", background=True)
        terminal = next(iter(sandbox.terminals.values()))
        try:
            assert result.success is True
            assert terminal.process is not None
            assert os.getpgid(terminal.process.pid) == terminal.process.pid
            assert terminal.log_path is not None
            for _ in range(20):
                if Path(terminal.log_path).read_text(encoding="utf-8") == "ready\n":
                    break
                await asyncio.sleep(0.05)
            assert Path(terminal.log_path).read_text(encoding="utf-8") == "ready\n"
        finally:
            await terminal.stop()

    asyncio.run(exercise())


def test_reconnect_restores_a_live_persisted_preview(tmp_path, monkeypatch):
    monkeypatch.setattr(sandbox_manager, "SANDBOX_BASE_DIR", str(tmp_path))
    listener = socket.socket()
    listener.bind(("127.0.0.1", 0))
    listener.listen()
    port = listener.getsockname()[1]
    work_dir = tmp_path / "persisted"
    metadata = work_dir / ".pwc" / "preview.json"
    metadata.parent.mkdir(parents=True)
    metadata.write_text(
        json.dumps(
            {
                "schema": 1,
                "pid": os.getpid(),
                "port": port,
                "url": f"http://127.0.0.1:{port}",
                "log_path": str(work_dir / ".pwc" / "preview.log"),
            }
        ),
        encoding="utf-8",
    )

    async def exercise():
        sandbox = sandbox_manager.BoxLiteSandbox("persisted")
        await sandbox.reconnect()
        state = sandbox.preview_status()
        assert state.url == f"http://127.0.0.1:{port}"
        assert sandbox.state.status == sandbox_manager.SandboxStatus.RUNNING

    try:
        asyncio.run(exercise())
    finally:
        listener.close()


def test_macos_preview_is_submitted_to_launchd(tmp_path, monkeypatch):
    monkeypatch.setattr(sandbox_manager, "SANDBOX_BASE_DIR", str(tmp_path))
    monkeypatch.setattr(sys, "platform", "darwin")
    monkeypatch.setattr(sandbox_manager.shutil, "which", lambda name: "/bin/launchctl")

    async def exercise():
        sandbox = sandbox_manager.BoxLiteSandbox("launchd")
        sandbox.work_dir.mkdir(parents=True)
        calls = []

        async def kill_port(_port, max_attempts=10):
            return True

        async def install_dependencies(timeout=180.0):
            return CommandResult(
                success=True, exit_code=0, stdout="", stderr="", duration_ms=0
            )

        async def remove_launchd_job(label=None):
            return True

        async def execute(command, timeout=60.0, background=False):
            calls.append((command, background))
            return CommandResult(
                success=True, exit_code=0, stdout="", stderr="", duration_ms=0
            )

        monkeypatch.setattr(sandbox, "_kill_port", kill_port)
        monkeypatch.setattr(sandbox, "install_dependencies", install_dependencies)
        monkeypatch.setattr(sandbox, "_remove_launchd_job", remove_launchd_job)
        monkeypatch.setattr(sandbox, "exec", execute)
        monkeypatch.setattr(sandbox, "_port_is_listening", lambda _port: True)

        result = await sandbox.start_preview()

        assert result.success is True
        assert any("launchctl submit" in command for command, _ in calls)
        metadata = json.loads(
            (sandbox.work_dir / ".pwc" / "preview.json").read_text(encoding="utf-8")
        )
        assert metadata["supervisor"] == "launchctl"
        assert metadata["label"].startswith("com.perfectwebclone.preview.")

    asyncio.run(exercise())
