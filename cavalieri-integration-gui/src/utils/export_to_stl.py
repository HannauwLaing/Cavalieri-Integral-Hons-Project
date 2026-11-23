from pathlib import Path

import numpy as np
import trimesh
import io
import base64
import json

def export_cav3d_displays_to_stl(
    displays,
    output_path,
    *,
    xy_scale=1.0,
    z_scale=1.0,
    base_z=0.0,
    include_top=True,
    include_bottom=True,
    include_curtains=True,
    deduplicate_curtains=True,
    curtain_key_decimals=10,
):
    """
    Export display_cav3d output to a 3D-printable STL file.

    Parameters
    ----------
    displays:
        The list returned by display_cav3d(...).

    output_path:
        Where to save the STL file

    xy_scale:
        Scale factor for x and y coordinates.

    z_scale:
        Scale factor for z coordinates.

    base_z:
        Z-value used for the bottom mesh. Your Plotly code displays bot_mesh at z = 0,
        so this defaults to 0.0.

    include_top:
        Whether to include display.top_mesh.

    include_bottom:
        Whether to include display.bot_mesh as a flat base.

    include_curtains:
        Whether to include side curtain meshes.

    deduplicate_curtains:
        Removes internal/shared curtains, similar to your Plotly display code.
    """

    output_path = Path(output_path).name
    # output_path.parent.mkdir(parents=True, exist_ok=True)

    meshes = []

    for display in displays:
        if include_top:
            top_mesh = np.asarray(display.top_mesh, dtype=float)
            top_mesh = _scale_grid(top_mesh, xy_scale=xy_scale, z_scale=z_scale)
            meshes.append(_grid_to_trimesh(top_mesh, flip_faces=True))

        if include_bottom:
            bot_mesh = np.asarray(display.bot_mesh, dtype=float)
            bot_mesh = _force_grid_z(bot_mesh, base_z)
            bot_mesh = _scale_grid(bot_mesh, xy_scale=xy_scale, z_scale=z_scale)
            meshes.append(_grid_to_trimesh(bot_mesh, flip_faces=True))

    if include_curtains:
        curtains = _get_export_curtains(
            displays,
            deduplicate=deduplicate_curtains,
            decimals=curtain_key_decimals,
        )

        for curtain in curtains:
            curtain = np.asarray(curtain, dtype=float)
            curtain = _scale_grid(curtain, xy_scale=xy_scale, z_scale=z_scale)
            meshes.append(_grid_to_trimesh(curtain, flip_faces=False))

    final_mesh = trimesh.util.concatenate(meshes)
    final_mesh.process(validate=True)
    final_mesh.merge_vertices()
    # final_mesh.export()

    # final_mesh.export(output_path)
    buffer = io.BytesIO()
    final_mesh.export(buffer, file_type="stl")
    return _browser_download_script(buffer.getvalue(), output_path, "model/stl");
    # return buffer.getvalue()

def _grid_to_trimesh(grid, *, flip_faces=False):
    """
    Convert an (rows, cols, 3) grid of points into a triangle mesh.
    """

    if grid.ndim != 3 or grid.shape[2] != 3:
        raise ValueError(f"Expected grid shape (rows, cols, 3), got {grid.shape}")

    rows, cols, _ = grid.shape

    vertices = grid.reshape(-1, 3)
    faces = []

    def idx(i, j):
        return i * cols + j

    for i in range(rows - 1):
        for j in range(cols - 1):
            a = idx(i, j)
            b = idx(i, j + 1)
            c = idx(i + 1, j)
            d = idx(i + 1, j + 1)

            if flip_faces:
                faces.append([a, b, c])
                faces.append([b, d, c])
            else:
                faces.append([a, c, b])
                faces.append([b, c, d])

    return trimesh.Trimesh(
        vertices=vertices,
        faces=np.asarray(faces),
        process=False,
    )


def _force_grid_z(grid, z_value):
    """
    Convert bot_mesh into a real 3D grid.
    """

    if grid.ndim != 3:
        raise ValueError(f"Expected grid with 3 dimensions, got {grid.shape}")

    if grid.shape[2] == 2:
        z = np.full(grid.shape[:2] + (1,), z_value, dtype=float)
        return np.concatenate([grid, z], axis=2)

    if grid.shape[2] == 3:
        out = grid.copy()
        out[..., 2] = z_value
        return out

    raise ValueError(f"Expected last dimension 2 or 3, got {grid.shape}")


def _scale_grid(grid, *, xy_scale, z_scale):
    out = grid.copy()
    out[..., 0] *= xy_scale
    out[..., 1] *= xy_scale
    out[..., 2] *= z_scale
    return out


def _get_export_curtains(displays, *, deduplicate, decimals):
    """
    Recreates curtain_id_map logic.

    Shared/internal curtains appear more than once. Removes internal curtains to only get the outer curtains.
    """

    if not deduplicate:
        curtains = []
        for display in displays:
            curtains.extend(np.asarray(display.curtains))
        return curtains

    curtain_map = {}

    for display in displays:
        for curtain in np.asarray(display.curtains):
            a = curtain[-1, 0, :]
            b = curtain[-1, -1, :]

            key = _curtain_key(a, b, decimals)

            if key in curtain_map:
                curtain_map[key][0] += 1
            else:
                curtain_map[key] = [0, curtain]

    export_curtains = []

    for repetitions, curtain in curtain_map.values():
        if repetitions == 0:
            export_curtains.append(curtain)

    return export_curtains


def _curtain_key(a, b, decimals):
    """
    Creates a stable key for a curtain edge, independent of direction.
    """

    a = tuple(np.round(a, decimals))
    b = tuple(np.round(b, decimals))

    return tuple(sorted([a, b]))


def _browser_download_script(data, filename, mime ):
    if isinstance(data, str):
        data = data.encode("utf-8")
    b64 = base64.b64encode(data).decode("ascii")

    return f"""
        <script>
            (() => {{
                const b64 = "{b64}";
                const byteCharacters = atob(b64);
                const byteNumbers = new Array(byteCharacters.length);

                for (let i = 0; i < byteCharacters.length; i++) {{
                    byteNumbers[i] = byteCharacters.charCodeAt(i);
                }}

                const byteArray = new Uint8Array(byteNumbers);
                const blob = new Blob([byteArray], {{ type: {json.dumps(mime)} }});

                const url = URL.createObjectURL(blob);
                const a = document.createElement("a");

                a.href = url;
                a.download = {json.dumps(filename)};
                document.body.appendChild(a);
                a.click();

                a.remove();
                setTimeout(() => URL.revokeObjectURL(url), 1000);
            }})();
        </script>
        """
