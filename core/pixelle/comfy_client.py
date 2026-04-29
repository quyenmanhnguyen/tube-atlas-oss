"""HTTP client for ComfyUI (local-first, RunningHub cloud fallback).

Minimal surface for PR-A1 — just enough to:

1. Probe whether a ComfyUI server is reachable at the configured local URL.
2. Submit a workflow JSON for execution and poll until done (local).
3. Submit a workflow to RunningHub cloud as a fallback.

The actual workflow JSONs and the higher-level ``generate_image`` /
``generate_video`` helpers will land in PR-A2 (alongside the Producer page).
This module deliberately stays small so it's easy to test without a live
ComfyUI instance.
"""
from __future__ import annotations

from dataclasses import dataclass

import requests

from core.pixelle.config import ComfyUIConfig


class ComfyUIError(RuntimeError):
    """Raised when both local and cloud ComfyUI fail to respond."""


@dataclass
class ComfyEndpoint:
    """Resolved endpoint after the local-first / cloud-fallback decision."""

    kind: str  # "local" or "runninghub"
    base_url: str


def resolve_endpoint(config: ComfyUIConfig, *, timeout: float = 2.0) -> ComfyEndpoint:
    """Pick the best available ComfyUI endpoint.

    Order:

    1. If ``cloud_only`` is set → use RunningHub (require key).
    2. Otherwise try ``local_url`` first; if it responds → use it.
    3. Otherwise fall back to RunningHub if a key is configured.
    4. Else raise :class:`ComfyUIError`.
    """
    if config.cloud_only:
        if not config.cloud_available:
            raise ComfyUIError(
                "cloud_only=True but RUNNINGHUB_API_KEY is not set."
            )
        return ComfyEndpoint(kind="runninghub", base_url=config.runninghub_base_url)

    if _is_local_alive(config.local_url, timeout=timeout):
        return ComfyEndpoint(kind="local", base_url=config.local_url)

    if config.cloud_available:
        return ComfyEndpoint(kind="runninghub", base_url=config.runninghub_base_url)

    raise ComfyUIError(
        f"ComfyUI not reachable at {config.local_url} and no RunningHub key set."
    )


def _is_local_alive(base_url: str, *, timeout: float) -> bool:
    """Cheap readiness probe — ``GET /system_stats``.

    ComfyUI exposes ``/system_stats`` since v0.0.3; a 200 response means
    the server is up and accepting requests.
    """
    try:
        resp = requests.get(f"{base_url.rstrip('/')}/system_stats", timeout=timeout)
        return resp.status_code == 200
    except requests.RequestException:
        return False


def submit_local_workflow(
    base_url: str,
    workflow: dict,
    *,
    client_id: str = "tube-atlas",
    timeout: float = 30.0,
) -> str:
    """Queue a workflow on a **local** ComfyUI server.

    Returns the ``prompt_id`` assigned by ComfyUI (caller can poll
    ``/history/{prompt_id}`` to retrieve outputs). PR-A2 will add the
    poll + output-fetch helpers.
    """
    payload = {"prompt": workflow, "client_id": client_id}
    resp = requests.post(
        f"{base_url.rstrip('/')}/prompt", json=payload, timeout=timeout
    )
    resp.raise_for_status()
    data = resp.json()
    prompt_id = data.get("prompt_id")
    if not prompt_id:
        raise ComfyUIError(f"ComfyUI /prompt returned no prompt_id: {data!r}")
    return prompt_id


def submit_runninghub_task(
    workflow_id: str,
    *,
    api_key: str,
    inputs: dict,
    instance: str = "",
    timeout: float = 30.0,
    base_url: str = "https://www.runninghub.cn",
) -> str:
    """Queue a workflow on RunningHub cloud.

    See https://www.runninghub.ai/docs for the live API spec. PR-A1 only
    issues the create-task call; polling lands in PR-A2.
    """
    payload: dict[str, object] = {
        "apiKey": api_key,
        "workflowId": workflow_id,
        "nodeInfoList": _to_node_info_list(inputs),
    }
    if instance:
        payload["instanceType"] = instance
    resp = requests.post(
        f"{base_url.rstrip('/')}/task/openapi/create",
        json=payload,
        timeout=timeout,
    )
    resp.raise_for_status()
    data = resp.json()
    task_id = (data.get("data") or {}).get("taskId")
    if not task_id:
        raise ComfyUIError(f"RunningHub create-task returned no taskId: {data!r}")
    return str(task_id)


def _to_node_info_list(inputs: dict) -> list[dict]:
    """Convert ``{node_id: {field: value}}`` to RunningHub's flat list shape."""
    out: list[dict] = []
    for node_id, fields in inputs.items():
        for field_name, field_value in fields.items():
            out.append(
                {
                    "nodeId": str(node_id),
                    "fieldName": field_name,
                    "fieldValue": field_value,
                }
            )
    return out
