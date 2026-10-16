
# simisa

[![GitHub release (latest by date)](https://img.shields.io/github/v/release/pgroenbaek/simisa?style=flat&label=Latest%20Version)](https://github.com/pgroenbaek/simisa/releases)
[![Python 3.8+](https://img.shields.io/badge/Python-3.8%2B-blue?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![License GNU GPL v3](https://img.shields.io/badge/License-%20%20GNU%20GPL%20v3%20-lightgrey?style=flat&logo=data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCA2NDAgNTEyIj4KICA8IS0tIEZvbnQgQXdlc29tZSBGcmVlIDYuNy4yIGJ5IEBmb250YXdlc29tZSAtIGh0dHBzOi8vZm9udGF3ZXNvbWUuY29tIExpY2Vuc2UgLSBodHRwczovL2ZvbnRhd2Vzb21lLmNvbS9saWNlbnNlL2ZyZWUgQ29weXJpZ2h0IDIwMjUgRm9udGljb25zLCBJbmMuIC0tPgogIDxwYXRoIGZpbGw9IndoaXRlIiBkPSJNMzg0IDMybDEyOCAwYzE3LjcgMCAzMiAxNC4zIDMyIDMycy0xNC4zIDMyLTMyIDMyTDM5OC40IDk2Yy01LjIgMjUuOC0yMi45IDQ3LjEtNDYuNCA1Ny4zTDM1MiA0NDhsMTYwIDBjMTcuNyAwIDMyIDE0LjMgMzIgMzJzLTE0LjMgMzItMzIgMzJsLTE5MiAwLTE5MiAwYy0xNy43IDAtMzItMTQuMy0zMi0zMnMxNC4zLTMyIDMyLTMybDE2MCAwIDAtMjk0LjdjLTIzLjUtMTAuMy00MS4yLTMxLjYtNDYuNC01Ny4zTDEyOCA5NmMtMTcuNyAwLTMyLTE0LjMtMzItMzJzMTQuMy0zMiAzMi0zMmwxMjggMGMxNC42LTE5LjQgMzcuOC0zMiA2NC0zMnM0OS40IDEyLjYgNjQgMzJ6bTU1LjYgMjg4bDE0NC45IDBMNTEyIDE5NS44IDQzOS42IDMyMHpNNTEyIDQxNmMtNjIuOSAwLTExNS4yLTM0LTEyNi03OC45Yy0yLjYtMTEgMS0yMi4zIDYuNy0zMi4xbDk1LjItMTYzLjJjNS04LjYgMTQuMi0xMy44IDI0LjEtMTMuOHMxOS4xIDUuMyAyNC4xIDEzLjhsOTUuMiAxNjMuMmM1LjcgOS44IDkuMyAyMS4xIDYuNyAzMi4xQzYyNy4yIDM4MiA1NzQuOSA0MTYgNTEyIDQxNnpNMTI2LjggMTk1LjhMNTQuNCAzMjBsMTQ0LjkgMEwxMjYuOCAxOTUuOHpNLjkgMzM3LjFjLTIuNi0xMSAxLTIyLjMgNi43LTMyLjFsOTUuMi0xNjMuMmM1LTguNiAxNC4yLTEzLjggMjQuMS0xMy44czE5LjEgNS4zIDI0LjEgMTMuOGw5NS4yIDE2My4yYzUuNyA5LjggOS4zIDIxLjEgNi43IDMyLjFDMjQyIDM4MiAxODkuNyA0MTYgMTI2LjggNDE2UzExLjcgMzgyIC45IDMzNy4xeiIvPgo8L3N2Zz4=&logoColor=%23ffffff)](https://github.com/pgroenbaek/simisa/blob/master/LICENSE)

A Python module to read and write files used with MSTS and Open Rails.

This module has a similar API to Python's built-in `json` module. When loading files, this module handles compression and text/binary formats of the SIMISA container seamlessly.

It's also not sensitive to whitespace and formatting in STF text files at all.

## Installation

### Install from PyPI

```sh
pip install --upgrade simisa
```

### Install from wheel

If you have downloaded a `.whl` file from the [Releases](https://github.com/pgroenbaek/simisa/releases) page, install it with:

```sh
pip install path/to/simisa-<version>‑py3‑none‑any.whl
```

Replace `<version>` with the actual version number in the filename.

### Install from source

```sh
git clone https://github.com/pgroenbaek/simisa.git
pip install --upgrade ./simisa
```

## Usage

Not all file types used with MSTS and Open Rails are currently implemented. You can find the list of supported file types in the table below.

| Shorthand  | Full module name | File type               | Read files | Write files |
| ---------- | ---------------- | ----------------------- | ---------- | ----------- |
| `s`        | `shape`          | `.s`                    | Yes        | Yes         |
| `t`        | `terrain`        | `.t`                    | Yes        | Yes         |
| `w`        | `world`          | `.w`                    | Yes        | Yes         |
| `rdb`      | `roaddatabase`   | `.rdb`                  | Yes        | No          |
| `tdb`      | `trackdatabase`  | `.tdb`                  | Yes        | No          |
| `tsection` | `tracksections`  | `.dat` (`tsection.dat`) | Yes        | No          |

When loading files, the module seamlessly takes care of handling compression and text/binary format based on the information in the file header.

### Reading files

```python
from simisa import s, t, w, rdb, tdb, tsection

shape_obj = s.load("path/to/shapefile.s")
terrain_obj = t.load("path/to/terrainfile.t")
world_obj = w.load("path/to/worldfile.w")
rdb_obj = rdb.load("path/to/roaddatabasefile.rdb")
tdb_obj = tdb.load("path/to/trackdatabasefile.tdb")
tsection_obj = tsection.load("path/to/tsection.dat")
```

```python
from simisa import s, t, w, rdb, tdb, tsection

shape_obj = s.loads(shape_text)
terrain_obj = t.loads(terrain_text)
world_obj = w.loads(world_text)
rdb_obj = rdb.loads(rdb_text)
tdb_obj = tdb.loads(tdb_text)
tsection_obj = tsection.loads(tsection_text)
```

### Writing files

#### Uncompressed

```python
from simisa import s, t, w

s.dump(shape_obj, "path/to/shapefile.s")
t.dump(terrain_obj, "path/to/terrainfile.t")
w.dump(world_obj, "path/to/worldfile.w")
```

```python
from simisa import s, t, w

shape_text = s.dumps(shape_obj)
terrain_text = t.dumps(terrain_obj)
world_text = w.dumps(world_obj)
```

#### Compressed

Writing files compressed:

```python
from simisa import s, t, w

s.dump(shape_file, "path/to/shapefile.s", compressed=True)
t.dump(terrain_file, "path/to/terrainfile.t", compressed=True)
w.dump(world_file, "path/to/worldfile.w", compressed=True)
```

### Accessing the object trees

```python
from simisa import shape

shape_obj = shape.load("path/to/shapefile.s")

print(shape_obj)
print(len(shape_obj.points))
print(shape_obj.lod_controls[2].lod_dlevel)
```

```python
>>> print(shape_obj)
Shape(shape_header=ShapeHeader(flags1=0, flags2=0), volumes (len=12), shader_names (len=2), texture_filter_names (len=2), points (len=3962), uv_points (len=1841), normals (len=2725), sort_vectors (len=11), colours (len=0), matrices (len=10), images (len=11), textures (len=15), light_materials (len=0), light_model_cfgs (len=1), vtx_states (len=12), prim_states (len=30), lod_controls (len=1), animations (len=1))
>>> print(len(shape_obj.points))
3962
>>> print(shape_obj.lod_controls[0].distance_levels[2])
DistanceLevel(distance_level_header=DistanceLevelHeader(dlevel_selection=800.0, hierarchy (len=10)), sub_objects (len=1))
>>> print(len(shape_obj.lod_controls[0].distance_levels[2].sub_objects[0].vertices))
133
>>> print(len(shape_obj.lod_controls[0].distance_levels[2].sub_objects[0].primitives[0].indexed_trilist.vertex_idxs))
67
```

### Editing the object trees

```python
from simisa import shape
from simisa.shape import UVPoint

shape_obj = shape.load("path/to/shapefile.s")

# Empting the points list
shape_obj.points = []

# Adding a new UVPoint
new_uv_point = UVPoint(0.0, 1.0)
shape_obj.uv_points.append(new_uv_point)

shape.dump(shape_obj, "path/to/shapefile_edited.s")
```

### Checking header data

#### Compression

```python
import simisa

simisa.is_compressed("path/to/shapefile.s")
```

#### Reading file type and version

```python
import simisa

simisa.read_filetype("path/to/shapefile.s")
simisa.read_fileversion("path/to/shapefile.s")
```


#### Checking file format

```python
import simisa

simisa.is_unicode("path/to/shapefile.s")
simisa.is_text("path/to/shapefile.s")
simisa.is_binary("path/to/shapefile.s")
```



## Running Tests

You can run tests manually or use `tox` to test across multiple Python versions.

### Run Tests Manually
First, install the required dependencies:

```sh
pip install pytest
```

Then, run tests with:

```sh
pytest
```


### Run Tests with `tox`

First, install the required dependencies:

```sh
pip install tox pytest
```

Then, run tests with:

```sh
tox
```

This will execute tests for all Python versions specified in `tox.ini`.

## Contributing

Contributions of all kinds are welcome. These could be suggestions, issues, bug fixes, documentation improvements, or new features.

For more details see the [contribution guidelines](/CONTRIBUTING.md).


## License

The source code of this project is licensed under the [GNU General Public License v3.0 (GPL-3.0)](https://www.gnu.org/licenses/gpl-3.0.html). You are free to use, modify, and distribute the code under the terms of this license. See the [LICENSE](/LICENSE) file for the full license text.
