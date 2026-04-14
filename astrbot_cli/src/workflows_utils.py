"""Workflow management utilities for AstrBot CLI."""

import json
import subprocess
from pathlib import Path
from typing import Any

from .path_config import get_astrbot_root


def get_workflows_path() -> Path:
    """Get the user workflows directory path."""
    astrbot_root = get_astrbot_root()
    if astrbot_root:
        return astrbot_root / "data" / "workflows"
    return Path.cwd() / "data" / "workflows"


def get_builtin_workflows_path() -> Path:
    """Get the built-in workflows directory path (shipped with CLI)."""
    return Path(__file__).parent / "workflows"


def get_dagu_bin() -> str:
    """Get dagu binary path."""
    return "dagu"


def list_workflows() -> list[dict]:
    """List all workflow files.

    Includes both built-in workflows (shipped with CLI) and user workflows.

    Returns:
        List of workflow info dictionaries

    """
    workflows = []
    seen_names = set()

    # List built-in workflows first
    builtin_path = get_builtin_workflows_path()
    if builtin_path.exists():
        for file in builtin_path.glob("*.yaml"):
            name = file.stem
            seen_names.add(name)
            workflows.append({
                "name": name,
                "path": str(file),
                "exists": True,
                "builtin": True,
            })

    # List user workflows
    workflows_path = get_workflows_path()
    if workflows_path.exists():
        for file in workflows_path.glob("*.yaml"):
            name = file.stem
            if name not in seen_names:
                workflows.append({
                    "name": name,
                    "path": str(file),
                    "exists": True,
                    "builtin": False,
                })

    return workflows


def get_workflow_status(name: str) -> dict | None:
    """Get workflow running status.

    Args:
        name: Workflow name

    Returns:
        Status dict or None if not found

    """
    try:
        result = subprocess.run(
            [get_dagu_bin(), "status", name],
            capture_output=True,
            timeout=10,
        )
        # Decode with error handling to avoid UnicodeDecodeError
        stdout = result.stdout.decode("utf-8", errors="replace")
        stderr = result.stderr.decode("utf-8", errors="replace")
        if result.returncode == 0:
            return {"name": name, "status": "running", "output": stdout}
        return {"name": name, "status": "stopped", "output": stderr}
    except subprocess.TimeoutExpired:
        return {"name": name, "status": "timeout", "output": "Command timed out"}
    except FileNotFoundError:
        return {"name": name, "status": "error", "output": "dagu not found"}


def find_workflow_file(name: str) -> Path | None:
    """Find a workflow file by name.

    Checks both built-in and user workflows.

    Args:
        name: Workflow name

    Returns:
        Path to workflow file or None if not found

    """
    # Check user workflows first (higher priority)
    user_workflow = get_workflows_path() / f"{name}.yaml"
    if user_workflow.exists():
        return user_workflow

    # Check built-in workflows
    builtin_workflow = get_builtin_workflows_path() / f"{name}.yaml"
    if builtin_workflow.exists():
        return builtin_workflow

    return None


def start_workflow(name: str, params: list[str] | None = None) -> dict:
    """Start a workflow.

    Args:
        name: Workflow name
        params: Optional list of KEY=VALUE parameter strings

    Returns:
        Result dict with status

    """
    workflow_file = find_workflow_file(name)

    if not workflow_file:
        return {"success": False, "error": f"Workflow '{name}' not found"}

    # Build dagu command with parameters
    # dagu format: dagu start <dag> --params "KEY=VALUE KEY2=VALUE2"
    cmd = [get_dagu_bin(), "start", str(workflow_file)]
    if params:
        # Join all params into a single string for dagu
        params_str = " ".join(params)
        cmd.extend(["--params", params_str])

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            timeout=30,
        )
        stdout = result.stdout.decode("utf-8", errors="replace")
        stderr = result.stderr.decode("utf-8", errors="replace")
        if result.returncode == 0:
            return {"success": True, "output": stdout}
        return {"success": False, "error": stderr, "output": stdout}
    except subprocess.TimeoutExpired:
        return {"success": False, "error": "Command timed out"}
    except FileNotFoundError:
        return {"success": False, "error": "dagu not found. Please install dagu first."}


def stop_workflow(name: str) -> dict:
    """Stop a workflow.

    Args:
        name: Workflow name

    Returns:
        Result dict with status

    """
    try:
        result = subprocess.run(
            [get_dagu_bin(), "stop", name],
            capture_output=True,
            timeout=30,
        )
        stdout = result.stdout.decode("utf-8", errors="replace")
        stderr = result.stderr.decode("utf-8", errors="replace")
        if result.returncode == 0:
            return {"success": True, "output": stdout}
        return {"success": False, "error": stderr}
    except subprocess.TimeoutExpired:
        return {"success": False, "error": "Command timed out"}
    except FileNotFoundError:
        return {"success": False, "error": "dagu not found. Please install dagu first."}


def get_workflow_logs(name: str, lines: int = 50) -> dict:
    """Get workflow logs.

    Args:
        name: Workflow name
        lines: Number of lines to retrieve

    Returns:
        Result dict with logs

    """
    try:
        result = subprocess.run(
            [get_dagu_bin(), "logs", name, "--tail", str(lines)],
            capture_output=True,
            timeout=30,
        )
        stdout = result.stdout.decode("utf-8", errors="replace")
        return {"success": True, "logs": stdout}
    except subprocess.TimeoutExpired:
        return {"success": False, "error": "Command timed out"}
    except FileNotFoundError:
        return {"success": False, "error": "dagu not found"}


def create_workflow(name: str, description: str = "", commands: list[str] | None = None) -> dict:
    """Create a new workflow file.

    Args:
        name: Workflow name
        description: Workflow description
        commands: List of commands to execute

    Returns:
        Created workflow info

    """
    # Check if a built-in workflow with this name exists
    builtin_workflow = get_builtin_workflows_path() / f"{name}.yaml"
    if builtin_workflow.exists():
        return {"success": False, "error": f"Cannot overwrite built-in workflow '{name}'"}

    workflows_path = get_workflows_path()
    workflows_path.mkdir(parents=True, exist_ok=True)

    workflow_file = workflows_path / f"{name}.yaml"

    if workflow_file.exists():
        return {"success": False, "error": f"Workflow '{name}' already exists"}

    workflow_content = {
        "name": name,
        "description": description or f"AstrBot workflow: {name}",
        "steps": [],
    }

    if commands:
        for i, cmd in enumerate(commands, 1):
            workflow_content["steps"].append({
                "name": f"step-{i}",
                "command": cmd,
            })
    else:
        workflow_content["steps"].append({
            "name": "step-1",
            "command": "echo 'Hello from AstrBot workflow'",
        })

    workflow_file.write_text(
        f"""# AstrBot Workflow: {name}
# Edit this file to customize your workflow

name: {workflow_content['name']}
description: {workflow_content['description']}

steps:
""",
        encoding="utf-8",
    )

    for step in workflow_content["steps"]:
        workflow_file.write_text(
            f"""  - name: {step['name']}
    command: {step['command']}
""",
            encoding="utf-8",
            append=True,
        )

    return {
        "success": True,
        "name": name,
        "path": str(workflow_file),
    }
