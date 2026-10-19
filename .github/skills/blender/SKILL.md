---
name: blender
description: Inspect and modify the currently open Blender scene from the terminal via a local bridge, without MCP tool slots. USE FOR: reading the scene (objects, collections, tri counts, modifiers, UV/vertex groups), running Blender Python (bpy/bmesh) against the live session, querying the bundled offline Blender API and manual docs, capturing a viewport screenshot, checking game-asset readiness (scale applied, normals, topology, material count). DO NOT USE FOR: offline/headless batch work on files that are not open in Blender (run `blender --background` yourself), rendering pipelines with render farms, or editing .blend files while Blender is closed.
---

# Blender session bridge

Every call is a **shell command**, so this skill consumes zero tool slots. It talks
to the Blender MCP add-on's local socket (the same bridge the official
`blender-mcp` MCP server uses) at `localhost:9876`.

Never register `blender-mcp` as an MCP server: it exposes 26 tools and pushes the
model over its tool budget.

## Prerequisites

- Blender **5.1+** with the **MCP** add-on enabled (`Preferences → Add-ons`).
  The add-on starts the bridge automatically on Blender launch.
- If nothing answers, check the add-on's preferences: `Port` (default 9876) and
  `Auto Start` must be on. Only one Blender can own port 9876 at a time.

## Commands

Run from the workspace root (`python` must be on PATH):

```powershell
python .github/skills/blender/scripts/blender_cli.py ping
python .github/skills/blender/scripts/blender_cli.py summary
python .github/skills/blender/scripts/blender_cli.py detail Cube
python .github/skills/blender/scripts/blender_cli.py eval "<python>"
python .github/skills/blender/scripts/blender_cli.py eval -f scripts/check.py
python .github/skills/blender/scripts/blender_cli.py shot out.png
python .github/skills/blender/scripts/blender_cli.py docs api bevel --limit 10
python .github/skills/blender/scripts/blender_cli.py docs manual "uv unwrap" --limit 10
```

| Command | Returns |
|---|---|
| `ping` | `{"ok": true}` when the bridge is up |
| `summary` | scene name, unit scale, object count by type, 10 heaviest meshes by triangles, collections |
| `detail NAME` | transform, dimensions, modifiers, materials, mesh counts, UV layers, vertex groups, shape keys |
| `eval` | whatever dict you assign to `result` |
| `shot PATH` | writes a full-window PNG; **GUI only** |
| `docs api\|manual QUERY` | matching lines from the offline Blender 5.2 RST docs |

Environment overrides: `BLENDER_MCP_HOST`, `BLENDER_MCP_PORT`, `BLENDER_MCP_TIMEOUT`,
`BLENDER_MCP_DOCS`.

## Writing `eval` code

- The code runs inside Blender with `bpy` already available.
- Assign a **JSON-serializable dict** to `result`; anything else is rejected.
  Use names, not datablocks: `result = {"scale": list(obj.scale)}`.
- `print()` output comes back on stderr and is echoed to the terminal.
- Exceptions return a traceback; read the last line to see what failed.
- Operators need a valid context. Prefer direct data access (`obj.data`, `obj.modifiers`,
  `mesh.vertices`) over `bpy.ops` when you can.

## Recipes for the 3D study material

```powershell
# Triangle count for the whole scene
python .github/skills/blender/scripts/blender_cli.py eval "import bpy
total = 0
for obj in bpy.context.view_layer.objects:
    if obj.type == 'MESH':
        obj.data.calc_loop_triangles()
        total += len(obj.data.loop_triangles)
result = {'triangles': total}"

# Apply scale / rotation on the selected meshes (rule 1 of 3)
python .github/skills/blender/scripts/blender_cli.py eval "import bpy
bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
result = {'scale': [list(o.scale) for o in bpy.context.selected_objects]}"

# Recalculate normals outward on the active mesh (rule 2 of 3)
python .github/skills/blender/scripts/blender_cli.py eval "import bpy, bmesh
obj = bpy.context.view_layer.objects.active
bm = bmesh.new()
bm.from_mesh(obj.data)
bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
bm.to_mesh(obj.data)
bm.free()
result = {'normalized': obj.name}"

# Export the selection to glTF for Godot
python .github/skills/blender/scripts/blender_cli.py eval "import bpy
bpy.ops.export_scene.gltf(filepath=r'D:/Workspace/games/study/3d/out/prop.glb',
    export_format='GLB', use_selection=True, export_yup=True)
result = {'exported': True}"
```

## Reviewing an asset before export

Ask for `summary` and `detail` first, then check against the three rules in
`3d/README.md`:

1. `detail` shows `scale` ≈ `[1, 1, 1]` — otherwise scale is not applied.
2. `detail` mesh counts and `summary.heaviest_meshes` — decimate before exporting
   if the triangle count is far above the target.
3. `uv_layers` is non-empty and `materials` has as few entries as possible.

## Limitations

- The bridge needs a **running Blender**. For files that are not open, run
  `blender --background file.blend --python script.py` yourself.
- `shot` needs a GUI session; it fails under `--background`.
- `docs` searches plain text. Search with the bare symbol (`bevel`, `unwrap`),
  not a qualified path (`bmesh.ops.bevel` has no literal match in the RST).
- Port 9876 is a hard-coded default. Two Blender instances collide, and on Windows
  the second one may bind silently — change the port in the add-on preferences.

## Safety

`eval` executes arbitrary Python inside Blender with no sandbox. Treat any code
generated by a model as untrusted: read it before running it, and never point
this at a machine holding data you cannot afford to lose.
