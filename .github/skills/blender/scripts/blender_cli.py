"""Drive a running Blender session from the terminal.

This talks to the Blender MCP add-on's local socket directly (the same bridge
the official `blender-mcp` MCP server uses), so no MCP client and no tool
registration are involved: every call is just a shell command.

Request wire format (see the add-on's mcp_to_blender_server.py):
    {"type": "execute", "code": "<python>", "strict_json": true} + b"\\0"
Response:
    {"status": "ok"|"error", "result": {...}, "stdout": "...", "stderr": "..."} + b"\\0"

The executed code may assign a dict to `result`, which is echoed back as JSON.

Environment:
    BLENDER_MCP_HOST     default localhost
    BLENDER_MCP_PORT     default 9876
    BLENDER_MCP_TIMEOUT  default 300 seconds
    BLENDER_MCP_DOCS     override the bundled RST documentation directory
"""

from __future__ import annotations

import argparse
import json
import os
import socket
import sys

DEFAULT_PORT = 9876
RECV_BUFFER_SIZE = 65536

SUMMARY_CODE = """
import bpy
scene = bpy.context.scene
view_layer = bpy.context.view_layer
objects = list(view_layer.objects)

def tri_count(obj):
    if obj.type != 'MESH':
        return 0
    mesh = obj.data
    mesh.calc_loop_triangles()
    return len(mesh.loop_triangles)

by_type = {}
for obj in objects:
    by_type[obj.type] = by_type.get(obj.type, 0) + 1

heaviest = sorted(
    ({"name": obj.name, "tris": tri_count(obj)} for obj in objects if obj.type == 'MESH'),
    key=lambda item: item["tris"],
    reverse=True,
)[:10]

collections = []
def walk(layer_collection, depth):
    collections.append({
        "name": layer_collection.collection.name,
        "objects": sorted(obj.name for obj in layer_collection.collection.objects),
    })
    for child in layer_collection.children:
        walk(child, depth + 1)

walk(view_layer.layer_collection, 0)

active = view_layer.objects.active
result = {
    "scene": scene.name,
    "unit_scale": scene.unit_settings.scale_length,
    "object_count": len(objects),
    "objects_by_type": by_type,
    "heaviest_meshes": heaviest,
    "collections": collections,
    "active_object": active.name if active else None,
    "mode": bpy.context.mode,
    "camera": scene.camera.name if scene.camera else None,
}
"""

DETAIL_CODE = """
import bpy

obj = bpy.data.objects.get({name!r})
if obj is None:
    result = {{"error": "no object named {name}"}}
else:
    info = {{
        "name": obj.name,
        "type": obj.type,
        "parent": obj.parent.name if obj.parent else None,
        "location": [round(value, 4) for value in obj.location],
        "rotation_euler_deg": [round(value * 57.29578, 2) for value in obj.rotation_euler],
        "scale": [round(value, 4) for value in obj.scale],
        "dimensions": [round(value, 4) for value in obj.dimensions],
        "modifiers": [{{"name": mod.name, "type": mod.type}} for mod in obj.modifiers],
        "materials": [slot.material.name if slot.material else None for slot in obj.material_slots],
        "visible": obj.visible_get(),
    }}
    if obj.type == 'MESH':
        mesh = obj.data
        mesh.calc_loop_triangles()
        info["mesh"] = {{
            "vertices": len(mesh.vertices),
            "edges": len(mesh.edges),
            "polygons": len(mesh.polygons),
            "triangles": len(mesh.loop_triangles),
            "uv_layers": [layer.name for layer in mesh.uv_layers],
            "vertex_groups": [group.name for group in obj.vertex_groups],
            "shape_keys": [key.name for key in mesh.shape_keys.key_blocks] if mesh.shape_keys else [],
        }}
    result = info
"""

SCREENSHOT_CODE = """
import bpy

bpy.ops.screen.screenshot(filepath={path!r}, full=True)
result = {{"saved": {path!r}}}
"""


def _connection_params() -> tuple[str, int]:
    host = os.environ.get("BLENDER_MCP_HOST", "localhost")
    port = int(os.environ.get("BLENDER_MCP_PORT", str(DEFAULT_PORT)))
    return host, port


def send_code(code: str, *, timeout: float) -> dict[str, object]:
    host, port = _connection_params()
    request = json.dumps({"type": "execute", "code": code, "strict_json": True}) + "\0"
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(timeout)
            sock.connect((host, port))
            sock.sendall(request.encode("utf-8"))
            buffer = bytearray()
            while b"\0" not in buffer:
                chunk = sock.recv(RECV_BUFFER_SIZE)
                if not chunk:
                    break
                buffer.extend(chunk)
    except ConnectionRefusedError:
        raise SystemExit(
            "Cannot reach Blender at {:s}:{:d}. Start Blender and make sure the MCP add-on "
            "server is running (it auto-starts when the add-on is enabled).".format(host, port)
        )
    except socket.timeout:
        raise SystemExit("Blender did not answer within {:.0f}s at {:s}:{:d}".format(timeout, host, port))

    line = bytes(buffer).partition(b"\0")[0]
    if not line:
        raise SystemExit("Empty response from Blender")
    return json.loads(line.decode("utf-8"))


def run(code: str, *, timeout: float) -> dict[str, object]:
    response = send_code(code, timeout=timeout)
    stdout = response.get("stdout")
    stderr = response.get("stderr")
    if stdout:
        sys.stderr.write(stdout if stdout.endswith("\n") else stdout + "\n")
    if stderr:
        sys.stderr.write(stderr if stderr.endswith("\n") else stderr + "\n")
    if response.get("status") != "ok":
        raise SystemExit(str(response.get("message", response)))
    return response.get("result") or {}


def _docs_dir() -> str | None:
    override = os.environ.get("BLENDER_MCP_DOCS")
    if override:
        return override if os.path.isdir(override) else None
    appdata = os.environ.get("APPDATA")
    if appdata:
        candidate = os.path.join(appdata, "uv", "tools", "blender-mcp", "Lib", "site-packages", "blmcp", "data")
        if os.path.isdir(candidate):
            return candidate
    return None


def search_docs(topic: str, query: str, limit: int) -> list[str]:
    base = _docs_dir()
    if base is None:
        raise SystemExit(
            "Bundled Blender docs not found. Set BLENDER_MCP_DOCS to a directory of .rst files, "
            "or consult https://docs.blender.org/api/current/ online."
        )
    directory = os.path.join(base, topic)
    if not os.path.isdir(directory):
        raise SystemExit("No documentation topic named {!r} (expected {:s})".format(topic, directory))

    needle = query.lower()
    hits: list[str] = []
    for root, _dirs, files in os.walk(directory):
        for name in sorted(files):
            if not name.endswith(".rst"):
                continue
            path = os.path.join(root, name)
            try:
                with open(path, encoding="utf-8", errors="replace") as handle:
                    for number, line in enumerate(handle, 1):
                        if needle in line.lower():
                            relative = os.path.relpath(path, base)
                            hits.append("{:s}:{:d}: {:s}".format(relative, number, line.strip()[:160]))
                            if len(hits) >= limit:
                                return hits
            except OSError:
                continue
    return hits


def main() -> int:
    parser = argparse.ArgumentParser(description="Control a running Blender session over its local MCP bridge.")
    parser.add_argument("--timeout", type=float, default=float(os.environ.get("BLENDER_MCP_TIMEOUT", "300")))
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("ping", help="check that Blender is reachable")

    subparsers.add_parser("summary", help="scene overview: types, tri counts, collections")

    detail = subparsers.add_parser("detail", help="details for one object")
    detail.add_argument("name")

    evaluate = subparsers.add_parser("eval", help="execute Python in Blender; assign a dict to `result`")
    evaluate.add_argument("code", nargs="?")
    evaluate.add_argument("-f", "--file", help="read the code from a file")

    shot = subparsers.add_parser("shot", help="save a full-window screenshot (GUI mode only)")
    shot.add_argument("path")

    docs = subparsers.add_parser("docs", help="grep the bundled Blender API/manual docs")
    docs.add_argument("topic", choices=["api", "manual"])
    docs.add_argument("query")
    docs.add_argument("--limit", type=int, default=20)

    args = parser.parse_args()

    if args.command == "ping":
        result = run("result = {'ok': True}", timeout=args.timeout)
        print(json.dumps(result, ensure_ascii=False))
        return 0

    if args.command == "summary":
        result = run(SUMMARY_CODE, timeout=args.timeout)
    elif args.command == "detail":
        result = run(DETAIL_CODE.format(name=args.name), timeout=args.timeout)
    elif args.command == "shot":
        result = run(SCREENSHOT_CODE.format(path=args.path), timeout=args.timeout)
    elif args.command == "eval":
        if args.file:
            with open(args.file, encoding="utf-8") as handle:
                code = handle.read()
        elif args.code:
            code = args.code
        elif not sys.stdin.isatty():
            code = sys.stdin.read()
        else:
            raise SystemExit("Provide code as an argument, with -f FILE, or on stdin")
        result = run(code, timeout=args.timeout)
    elif args.command == "docs":
        hits = search_docs(args.topic, args.query, args.limit)
        if not hits:
            print("no matches for {!r}".format(args.query))
        else:
            print("\n".join(hits))
        return 0
    else:
        return 2

    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
