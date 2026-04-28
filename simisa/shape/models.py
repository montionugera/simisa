"""
This file is part of Simisa.

Copyright (C) 2026 Peter Grønbæk Andersen <peter@grnbk.io>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <https://www.gnu.org/licenses/>.
"""

import numpy as np
from abc import ABC
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class Vector:
    x: float
    y: float
    z: float

    def __repr__(self):
        return f"Vector(x={self.x}, y={self.y}, z={self.z})"

    def to_numpy(self) -> np.ndarray:
        return np.array([self.x, self.y, self.z])

    @classmethod
    def from_numpy(cls, array: np.ndarray):
        if array.shape != (3,):
            raise ValueError("Input array must have shape (3,).")
        return cls(array[0], array[1], array[2])

@dataclass
class Point:
    x: float
    y: float
    z: float

    def __repr__(self):
        return f"Point(x={self.x}, y={self.y}, z={self.z})"

    def to_numpy(self) -> np.ndarray:
        return np.array([self.x, self.y, self.z])

    @classmethod
    def from_numpy(cls, array: np.ndarray):
        if array.shape != (3,):
            raise ValueError("Input array must have shape (3,).")
        return cls(array[0], array[1], array[2])

@dataclass
class UVPoint:
    u: float
    v: float

    def __repr__(self):
        return f"UVPoint(u={self.u}, v={self.v})"

    def to_numpy(self) -> np.ndarray:
        return np.array([self.u, self.v])

    @classmethod
    def from_numpy(cls, array: np.ndarray):
        if array.shape != (2,):
            raise ValueError("Input array must have shape (2,).")
        return cls(array[0], array[1])

@dataclass
class Colour:
    a: float
    r: float
    g: float
    b: float

    def __repr__(self):
        return f"Colour(a={self.a}, r={self.r}, g={self.g}, b={self.b})"

@dataclass
class Matrix:
    name: str
    ax: float
    ay: float
    az: float
    bx: float
    by: float
    bz: float
    cx: float
    cy: float
    cz: float
    dx: float
    dy: float
    dz: float

    def __repr__(self):
        return (
            "Matrix(\n"
            f"  name='{self.name}',\n"
            f"  ax={self.ax}, ay={self.ay}, az={self.az},\n"
            f"  bx={self.bx}, by={self.by}, bz={self.bz},\n"
            f"  cx={self.cx}, cy={self.cy}, cz={self.cz},\n"
            f"  dx={self.dx}, dy={self.dy}, dz={self.dz}\n"
            ")"
        )

    def to_numpy(self) -> np.ndarray:
        """Convert to a 4x3 numpy matrix."""
        return np.array([
            [self.ax, self.ay, self.az],
            [self.bx, self.by, self.bz],
            [self.cx, self.cy, self.cz],
            [self.dx, self.dy, self.dz],
        ], dtype=np.float32)

    @classmethod
    def from_numpy(cls, name: str, array: np.ndarray):
        """Create a Matrix from a 4x3 numpy array."""
        if array.shape != (4, 3):
            raise ValueError("Input array must have shape (4, 3).")
        return cls(
            name,
            *array[0],
            *array[1],
            *array[2],
            *array[3],
        )

@dataclass
class VertexIdx:
    vertex1_index: int
    vertex2_index: int
    vertex3_index: int

    def __repr__(self):
        return (
            f"VertexIdx("
            f"vertex1_index={self.vertex1_index}, "
            f"vertex2_index={self.vertex2_index}, "
            f"vertex3_index={self.vertex3_index})"
        )

@dataclass
class NormalIdx:
    index: int
    unknown2: int

    def __repr__(self):
        return (
            f"NormalIdx("
            f"index={self.index}, "
            f"unknown2={self.unknown2})"
        )

@dataclass
class IndexedTrilist:
    vertex_idxs: List[VertexIdx]
    normal_idxs: List[NormalIdx]
    flags: List[str]

    def __repr__(self):
        return (
            "IndexedTrilist("
            f"vertex_idxs (len={len(self.vertex_idxs)}), "
            f"normal_idxs (len={len(self.normal_idxs)}), "
            f"flags (len={len(self.flags)}))"
        )

@dataclass
class KeyPosition(ABC):
    frame: int
    
    def _base_repr(self):
        return f"frame={self.frame}"

    def __repr__(self):
        return f"KeyPosition({self._base_repr()})"

@dataclass
class Controller(ABC):
    keyframes: List[KeyPosition]
    
    def _base_repr(self):
        return f"keyframes (len={len(self.keyframes)})"

    def __repr__(self):
        return f"Controller({self._base_repr()})"

class TCBRot(Controller):
    keyframes: List[KeyPosition]

    def __repr__(self):
        return f"TCBRot({self._base_repr()})"

@dataclass
class SlerpRot(KeyPosition):
    frame: int
    x: float
    y: float
    z: float
    w: float
    
    def __repr__(self):
        return (
            f"SlerpRot({self._base_repr()}, "
            f"x={self.x}, y={self.y}, z={self.z}, w={self.w})"
        )

@dataclass
class LinearPos(Controller):
    keyframes: List[KeyPosition]

    def __repr__(self):
        return f"LinearPos({self._base_repr()})"

@dataclass
class LinearKey(KeyPosition):
    frame: int
    x: float
    y: float
    z: float

    def __repr__(self):
        return (
            f"LinearKey({self._base_repr()}, "
            f"x={self.x}, y={self.y}, z={self.z})"
        )

@dataclass
class TCBPos(Controller):
    keyframes: List[KeyPosition]

    def __repr__(self):
        return f"TCBPos({self._base_repr()})"

@dataclass
class TCBKey(KeyPosition):
    frame: int
    x: float
    y: float
    z: float
    w: float
    tension: float
    continuity: float
    bias: float
    ease_in: float
    ease_out: float

    def __repr__(self):
        return (
            f"TCBKey({self._base_repr()}, "
            f"x={self.x}, y={self.y}, z={self.z}, w={self.w}, "
            f"tension={self.tension}, continuity={self.continuity}, bias={self.bias}, "
            f"ease_in={self.ease_in}, ease_out={self.ease_out})"
        )

@dataclass
class AnimationNode:
    name: str
    controllers: List[Controller]

    def __repr__(self):
        return (
            f"AnimationNode(name={self.name}, "
            f"controllers (len={len(self.controllers)}))"
        )

@dataclass
class Animation:
    frame_rate: int
    anima_count: int
    frametion_nodes: List[AnimationNode]

    def __repr__(self):
        return (
            f"Animation(frame_count={self.frame_count}, "
            f"frame_rate={self.frame_rate}, "
            f"animation_nodes (len={len(self.animation_nodes)}))"
        )

@dataclass
class ShapeHeader:
    flags1: str
    flags2: Optional[str] = None

    def __repr__(self):
        parts = [
            f"flags1={self.flags1}",
        ]

        if self.flags2 is not None:
            parts.append(f"flags2={self.flags2}")

        return f"ShapeHeader({', '.join(parts)})"

@dataclass
class VolumeSphere:
    vector: Vector
    radius: float

    def __repr__(self):
        return f"VolumeSphere(vector={self.vector}, radius={self.radius})"

@dataclass
class Texture:
    image_index: int
    filter_mode: int
    mipmap_lod_bias: float
    border_colour: Optional[int] = None

    def __repr__(self):
        return (
            f"Texture(image_index={self.image_index}, filter_mode={self.filter_mode}, "
            f"mipmap_lod_bias={self.mipmap_lod_bias}, border_colour={self.border_colour})"
        )

@dataclass
class LightMaterial:
    flags: int
    diff_colour_index: int
    amb_colour_index: int
    spec_colour_index: int
    emissive_colour_index: int
    spec_power: float

    def __repr__(self):
        return (
            f"LightMaterial(flags={self.flags}, "
            f"diff_colour_index={self.diff_colour_index}, amb_colour_index={self.amb_colour_index}, "
            f"spec_colour_index={self.spec_colour_index}, emissive_colour_index={self.emissive_colour_index}, "
            f"spec_power={self.spec_power})"
        )

@dataclass
class UVOp(ABC):
    texture_address_mode: int

    def _base_repr(self):
        return f"texture_address_mode={self.texture_address_mode}"

    def __repr__(self):
        return f"UVOp({self._base_repr()})"

@dataclass
class UVOpCopy(UVOp):
    texture_address_mode: int
    source_uv_index: int

    def __repr__(self):
        return f"UVOpCopy({self._base_repr()}, source_uv_index={self.source_uv_index})"

@dataclass
class UVOpReflectMapFull(UVOp):
    texture_address_mode: int

    def __repr__(self):
        return f"UVOpReflectMapFull({self._base_repr()})"

@dataclass
class UVOpReflectMap(UVOp):
    texture_address_mode: int

    def __repr__(self):
        return f"UVOpReflectMap({self._base_repr()})"

@dataclass
class UVOpUniformScale(UVOp):
    texture_address_mode: int
    source_uv_index: int
    unknown3: int
    unknown4: int

    def __repr__(self):
        return (
            f"UVOpUniformScale({self._base_repr()}, source_uv_index={self.source_uv_index}, "
            f"unknown3={self.unknown3}, unknown4={self.unknown4})"
        )

@dataclass
class UVOpNonUniformScale(UVOp):
    texture_address_mode: int
    source_uv_index: int
    unknown3: int
    unknown4: int

    def __repr__(self):
        return (
            f"UVOpNonUniformScale({self._base_repr()}, source_uv_index={self.source_uv_index}, "
            f"unknown3={self.unknown3}, unknown4={self.unknown4})"
        )

@dataclass
class LightModelCfg:
    flags: int
    uv_ops: List[UVOp]

    def __repr__(self):
        return f"LightModelCfg(flags={self.flags}, uv_ops (len={len(self.uv_ops)}))"

@dataclass
class VtxState:
    flags: int
    matrix_index: int
    light_material_index: int
    light_model_cfg_index: int
    light_flags: int
    matrix2_index: Optional[int] = None

    def __repr__(self):
        return (
            f"VtxState(flags={self.flags}, matrix_index={self.matrix_index}, "
            f"light_material_index={self.light_material_index}, "
            f"light_model_cfg_index={self.light_model_cfg_index}, "
            f"light_flags={self.light_flags}, matrix2_index={self.matrix2_index})"
        )

@dataclass
class PrimState:
    name: str
    flags: int
    shader_index: int
    texture_indices: List[int]
    z_bias: float
    vtx_state_index: int
    alpha_test_mode: int
    light_cfg_index: int
    z_buffer_mode: int

    def __repr__(self):
        return (
            f"PrimState(name={self.name}, flags={self.flags}, shader_index={self.shader_index}, "
            f"texture_indices (len={len(self.texture_indices)}), z_bias={self.z_bias}, "
            f"vtx_state_index={self.vtx_state_index}, alpha_test_mode={self.alpha_test_mode}, "
            f"light_cfg_index={self.light_cfg_index}, z_buffer_mode={self.z_buffer_mode})"
        )

@dataclass
class DistanceLevelsHeader:
    dlevel_bias: int

    def __repr__(self):
        return f"DistanceLevelsHeader(dlevel_bias={self.dlevel_bias})"

@dataclass
class CullablePrims:
    num_prims: int
    num_flat_sections: int
    num_prim_indices: int

    def __repr__(self):
        return (
            f"CullablePrims(num_prims={self.num_prims}, "
            f"num_flat_sections={self.num_flat_sections}, "
            f"num_prim_indices={self.num_prim_indices})"
        )

@dataclass
class GeometryNode:
    tx_light_cmds: int
    node_x_tx_light_cmds: int
    trilists: int
    line_lists: int
    pt_lists: int
    cullable_prims: CullablePrims

    def __repr__(self):
        return (
            f"GeometryNode(tx_light_cmds={self.tx_light_cmds}, "
            f"node_x_tx_light_cmds={self.node_x_tx_light_cmds}, "
            f"trilists={self.trilists}, line_lists={self.line_lists}, "
            f"pt_lists={self.pt_lists}, cullable_prims={self.cullable_prims})"
        )

@dataclass
class GeometryInfo:
    face_normals: int
    tx_light_cmds: int
    node_x_tx_light_cmds: int
    trilist_indices: int
    line_list_indices: int
    node_x_trilist_indices: int
    trilists: int
    line_lists: int
    pt_lists: int
    node_x_trilists: int
    geometry_nodes: List[GeometryNode]
    geometry_node_map: List[int]

    def __repr__(self):
        return (
            f"GeometryInfo(face_normals={self.face_normals}, "
            f"tx_light_cmds={self.tx_light_cmds}, node_x_tx_light_cmds={self.node_x_tx_light_cmds}, "
            f"trilist_indices={self.trilist_indices}, line_list_indices={self.line_list_indices}, "
            f"node_x_trilist_indices={self.node_x_trilist_indices}, trilists={self.trilists}, "
            f"line_lists={self.line_lists}, pt_lists={self.pt_lists}, node_x_trilists={self.node_x_trilists}, "
            f"geometry_nodes (len={len(self.geometry_nodes)}), geometry_node_map (len={len(self.geometry_node_map)}))"
        )

@dataclass
class SubObjectHeader:
    flags: int
    sort_vector_index: int
    volume_index: int
    source_vtx_fmt_flags: int
    destination_vtx_fmt_flags: int
    geometry_info: GeometryInfo
    subobject_shaders: List[int]
    subobject_light_cfgs: List[int]
    subobject_id: int

    def __repr__(self):
        return (
            f"SubObjectHeader(flags={self.flags}, sort_vector_index={self.sort_vector_index}, "
            f"volume_index={self.volume_index}, source_vtx_fmt_flags={self.source_vtx_fmt_flags}, "
            f"destination_vtx_fmt_flags={self.destination_vtx_fmt_flags}, geometry_info={self.geometry_info}, "
            f"subobject_shaders (len={len(self.subobject_shaders)}), "
            f"subobject_light_cfgs (len={len(self.subobject_light_cfgs)}), "
            f"subobject_id={self.subobject_id})"
        )

@dataclass
class Vertex:
    flags: str
    point_index: int
    normal_index: int
    colour1: str
    colour2: str
    vertex_uvs: List[int]

    def __repr__(self):
        return (
            f"Vertex(flags={self.flags}, point_index={self.point_index}, normal_index={self.normal_index}, "
            f"colour1={self.colour1}, colour2={self.colour2}, vertex_uvs (len={len(self.vertex_uvs)}))"
        )

@dataclass
class VertexSet:
    vtx_state: int
    vtx_start_index: int
    vtx_count: int

    def __repr__(self):
        return (
            f"VertexSet(vtx_state={self.vtx_state}, vtx_start_index={self.vtx_start_index}, vtx_count={self.vtx_count})"
        )

@dataclass
class Primitive:
    prim_state_index: int
    indexed_trilist: IndexedTrilist

    def __repr__(self):
        return (
            f"Primitive(prim_state_index={self.prim_state_index}, "
            f"indexed_trilist={self.indexed_trilist})"
        )

@dataclass
class SubObject:
    sub_object_header: SubObjectHeader
    vertices: List[Vertex]
    vertex_sets: List[VertexSet]
    primitives: List[Primitive]

    def __repr__(self):
        return (
            f"SubObject(sub_object_header={self.sub_object_header}, "
            f"vertices (len={len(self.vertices)}), "
            f"vertex_sets (len={len(self.vertex_sets)}), "
            f"primitives (len={len(self.primitives)}))"
        )

@dataclass
class DistanceLevelHeader:
    dlevel_selection: int
    hierarchy: List[int]
    
    def __repr__(self):
        return (
            f"DistanceLevelHeader(dlevel_selection={self.dlevel_selection}, "
            f"hierarchy (len={len(self.hierarchy)}))"
        )

@dataclass
class DistanceLevel:
    distance_level_header: DistanceLevelHeader
    sub_objects: List[SubObject]

    def __repr__(self):
        return (
            f"DistanceLevel(distance_level_header={self.distance_level_header}, "
            f"sub_objects (len={len(self.sub_objects)}))"
        )

@dataclass
class LodControl:
    distance_levels_header: DistanceLevelsHeader
    distance_levels: List[DistanceLevel]

    def __repr__(self):
        return (
            f"LodControl(distance_levels_header={self.distance_levels_header}, "
            f"distance_levels (len={len(self.distance_levels)}))"
        )

@dataclass
class Shape:
    shape_header: ShapeHeader
    volumes: List[VolumeSphere]
    shader_names: List[str]
    texture_filter_names: List[str]
    points: List[Point]
    uv_points: List[UVPoint]
    normals: List[Vector]
    sort_vectors: List[Vector]
    colours: List[Colour]
    matrices: List[Matrix]
    images: List[str]
    textures: List[Texture]
    light_materials: List[LightMaterial]
    light_model_cfgs: List[LightModelCfg]
    vtx_states: List[VtxState]
    prim_states: List[PrimState]
    lod_controls: List[LodControl]
    animations: Optional[List[Animation]] = None

    def __repr__(self):
        parts = [
            f"shape_header={self.shape_header}",
            f"volumes (len={len(self.volumes)})",
            f"shader_names (len={len(self.shader_names)})",
            f"texture_filter_names (len={len(self.texture_filter_names)})",
            f"points (len={len(self.points)})",
            f"uv_points (len={len(self.uv_points)})",
            f"normals (len={len(self.normals)})",
            f"sort_vectors (len={len(self.sort_vectors)})",
            f"colours (len={len(self.colours)})",
            f"matrices (len={len(self.matrices)})",
            f"images (len={len(self.images)})",
            f"textures (len={len(self.textures)})",
            f"light_materials (len={len(self.light_materials)})",
            f"light_model_cfgs (len={len(self.light_model_cfgs)})",
            f"vtx_states (len={len(self.vtx_states)})",
            f"prim_states (len={len(self.prim_states)})",
            f"lod_controls (len={len(self.lod_controls)})",
        ]

        if self.animations is not None:
            parts.append(f"animations (len={len(self.animations)})")

        return f"Shape({', '.join(parts)})"

