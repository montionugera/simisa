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

from .. import TokenID
from ..writer import BlockWriter
from .models import *


def dump(shape: Shape, filepath: str, compressed: bool = False) -> None:
    if not isinstance(shape, Shape):
        raise TypeError(f"Parameter 'shape' must be Shape, but got {type(shape).__name__}")

    if not isinstance(filepath, str):
        raise TypeError(f"Parameter 'filepath' must be str, but got {type(filepath).__name__}")

    if not isinstance(compressed, bool):
        raise TypeError(f"Parameter 'compressed' must be bool, but got {type(compressed).__name__}")

    with BlockWriter.open(
        filepath,
        filetype="s",
        fileversion="0",
        is_binary=compressed,
        is_unicode=not compressed,
        is_compressed=compressed
    ) as writer:
        write_shape(writer, shape)


def dumps(shape: Shape) -> str:
    if not isinstance(shape, Shape):
        raise TypeError(f"Parameter 'shape' must be Shape, but got {type(shape).__name__}")

    shape_text = BlockWriter.to_string(
        lambda writer: write_shape(writer, shape),
        filetype="s",
        fileversion="0"
    )

    return shape_text


def write_shape(writer: BlockWriter, shape: Shape) -> None:
    with writer.sub_block(TokenID.shape):
        write_shape_header(writer, shape.shape_header)
        write_volumes(writer, shape.volumes)
        write_shader_names(writer, shape.shader_names)
        write_texture_filter_names(writer, shape.texture_filter_names)
        write_points(writer, shape.points)
        write_uv_points(writer, shape.uv_points)
        write_normals(writer, shape.normals)
        write_sort_vectors(writer, shape.sort_vectors)
        write_colours(writer, shape.colours)
        write_matrices(writer, shape.matrices)
        write_images(writer, shape.images)
        write_textures(writer, shape.textures)
        write_light_materials(writer, shape.light_materials)
        write_light_model_cfgs(writer, shape.light_model_cfgs)
        write_vtx_states(writer, shape.vtx_states)
        write_prim_states(writer, shape.prim_states)
        write_lod_controls(writer, shape.lod_controls)

        if shape.animations is not None:
            write_animations(writer, shape.animations)


def write_shape_header(writer: BlockWriter, header: ShapeHeader) -> None:
    with writer.sub_block(TokenID.shape_header):
        writer.write_flags(header.flags1)
        if header.flags2 is not None:
            writer.write_flags(header.flags2)


def write_volumes(writer: BlockWriter, volumes: list) -> None:
    with writer.sub_block(TokenID.volumes):
        writer.write_count(len(volumes))
        for volume in volumes:
            with writer.sub_block(TokenID.vol_sphere):
                write_vector(writer, volume.vector)
                writer.write_float(volume.radius)


def write_vector(writer: BlockWriter, vector: Vector) -> None:
    with writer.sub_block(TokenID.vector):
        writer.write_float(vector.x)
        writer.write_float(vector.y)
        writer.write_float(vector.z)


def write_shader_names(writer: BlockWriter, shader_names: list) -> None:
    with writer.sub_block(TokenID.shader_names):
        writer.write_count(len(shader_names))
        for shader_name in shader_names:
            with writer.sub_block(TokenID.named_shader):
                writer.write_string(shader_name)


def write_texture_filter_names(writer: BlockWriter, filter_names: list) -> None:
    with writer.sub_block(TokenID.texture_filter_names):
        writer.write_count(len(filter_names))
        for filter_name in filter_names:
            with writer.sub_block(TokenID.named_filter_mode):
                writer.write_string(filter_name)


def write_points(writer: BlockWriter, points: list) -> None:
    with writer.sub_block(TokenID.points):
        writer.write_count(len(points))
        for point in points:
            with writer.sub_block(TokenID.point):
                writer.write_float(point.x)
                writer.write_float(point.y)
                writer.write_float(point.z)


def write_uv_points(writer: BlockWriter, uv_points: list) -> None:
    with writer.sub_block(TokenID.uv_points):
        writer.write_count(len(uv_points))
        for uv_point in uv_points:
            with writer.sub_block(TokenID.uv_point):
                writer.write_float(uv_point.u)
                writer.write_float(uv_point.v)


def write_normals(writer: BlockWriter, normals: list) -> None:
    with writer.sub_block(TokenID.normals):
        writer.write_count(len(normals))
        for normal in normals:
            write_vector(writer, normal)


def write_sort_vectors(writer: BlockWriter, sort_vectors: list) -> None:
    with writer.sub_block(TokenID.sort_vectors):
        writer.write_count(len(sort_vectors))
        for sort_vector in sort_vectors:
            write_vector(writer, sort_vector)


def write_colours(writer: BlockWriter, colours: list) -> None:
    with writer.sub_block(TokenID.colours):
        writer.write_count(len(colours))
        for colour in colours:
            with writer.sub_block(TokenID.colour):
                writer.write_float(colour.a)
                writer.write_float(colour.r)
                writer.write_float(colour.g)
                writer.write_float(colour.b)


def write_matrices(writer: BlockWriter, matrices: list) -> None:
    with writer.sub_block(TokenID.matrices):
        writer.write_count(len(matrices))
        for matrix in matrices:
            with writer.sub_block(TokenID.matrix, label=matrix.name):
                writer.write_float(matrix.ax)
                writer.write_float(matrix.ay)
                writer.write_float(matrix.az)
                writer.write_float(matrix.bx)
                writer.write_float(matrix.by)
                writer.write_float(matrix.bz)
                writer.write_float(matrix.cx)
                writer.write_float(matrix.cy)
                writer.write_float(matrix.cz)
                writer.write_float(matrix.dx)
                writer.write_float(matrix.dy)
                writer.write_float(matrix.dz)


def write_images(writer: BlockWriter, images: list) -> None:
    with writer.sub_block(TokenID.images):
        writer.write_count(len(images))
        for image in images:
            with writer.sub_block(TokenID.image):
                writer.write_string(image)


def write_textures(writer: BlockWriter, textures: list) -> None:
    with writer.sub_block(TokenID.textures):
        writer.write_count(len(textures))
        for texture in textures:
            with writer.sub_block(TokenID.texture):
                writer.write_int(texture.image_index)
                writer.write_int(texture.filter_mode)
                writer.write_float(texture.mipmap_lod_bias)
                if texture.border_colour is not None:
                    writer.write_flags(texture.border_colour)


def write_light_materials(writer: BlockWriter, light_materials: list) -> None:
    with writer.sub_block(TokenID.light_materials):
        writer.write_count(len(light_materials))
        for light_material in light_materials:
            with writer.sub_block(TokenID.light_material):
                writer.write_flags(light_material.flags)
                writer.write_int(light_material.diff_colour_index)
                writer.write_int(light_material.amb_colour_index)
                writer.write_int(light_material.spec_colour_index)
                writer.write_int(light_material.emissive_colour_index)
                writer.write_float(light_material.spec_power)


def write_light_model_cfgs(writer: BlockWriter, light_model_cfgs: list) -> None:
    with writer.sub_block(TokenID.light_model_cfgs):
        writer.write_count(len(light_model_cfgs))
        for light_model_cfg in light_model_cfgs:
            with writer.sub_block(TokenID.light_model_cfg):
                writer.write_flags(light_model_cfg.flags)
                write_uv_ops(writer, light_model_cfg.uv_ops)


def write_uv_ops(writer: BlockWriter, uv_ops: list) -> None:
    with writer.sub_block(TokenID.uv_ops):
        writer.write_count(len(uv_ops))
        for uv_op in uv_ops:
            if isinstance(uv_op, UVOpCopy):
                with writer.sub_block(TokenID.uv_op_copy):
                    writer.write_int(uv_op.texture_address_mode)
                    writer.write_int(uv_op.source_uv_index)
            elif isinstance(uv_op, UVOpReflectMapFull):
                with writer.sub_block(TokenID.uv_op_reflectmapfull):
                    writer.write_int(uv_op.texture_address_mode)
            elif isinstance(uv_op, UVOpReflectMap):
                with writer.sub_block(TokenID.uv_op_reflectmap):
                    writer.write_int(uv_op.texture_address_mode)
            elif isinstance(uv_op, UVOpUniformScale):
                with writer.sub_block(TokenID.uv_op_uniformscale):
                    writer.write_int(uv_op.texture_address_mode)
                    writer.write_int(uv_op.source_uv_index)
                    writer.write_int(uv_op.unknown3)
                    writer.write_int(uv_op.unknown4)
            elif isinstance(uv_op, UVOpNonUniformScale):
                with writer.sub_block(TokenID.uv_op_nonuniformscale):
                    writer.write_int(uv_op.texture_address_mode)
                    writer.write_int(uv_op.source_uv_index)
                    writer.write_int(uv_op.unknown3)
                    writer.write_int(uv_op.unknown4)


def write_vtx_states(writer: BlockWriter, vtx_states: list) -> None:
    with writer.sub_block(TokenID.vtx_states):
        writer.write_count(len(vtx_states))
        for vtx_state in vtx_states:
            with writer.sub_block(TokenID.vtx_state):
                writer.write_flags(vtx_state.flags)
                writer.write_int(vtx_state.matrix_index)
                writer.write_int(vtx_state.light_material_index)
                writer.write_int(vtx_state.light_model_cfg_index)
                writer.write_flags(vtx_state.light_flags)
                if vtx_state.matrix2_index is not None:
                    writer.write_int(vtx_state.matrix2_index)


def write_prim_states(writer: BlockWriter, prim_states: list) -> None:
    with writer.sub_block(TokenID.prim_states):
        writer.write_count(len(prim_states))
        for prim_state in prim_states:
            with writer.sub_block(TokenID.prim_state, label=prim_state.name):
                writer.write_flags(prim_state.flags)
                writer.write_int(prim_state.shader_index)
                write_tex_idxs(writer, prim_state.texture_indices)
                writer.write_float(prim_state.z_bias)
                writer.write_int(prim_state.vtx_state_index)
                writer.write_int(prim_state.alpha_test_mode)
                writer.write_int(prim_state.light_cfg_index)
                writer.write_int(prim_state.z_buffer_mode)


def write_tex_idxs(writer: BlockWriter, tex_idxs: list) -> None:
    with writer.sub_block(TokenID.tex_idxs):
        writer.write_count(len(tex_idxs))
        for tex_idx in tex_idxs:
            writer.write_int(tex_idx)


def write_lod_controls(writer: BlockWriter, lod_controls: list) -> None:
    with writer.sub_block(TokenID.lod_controls):
        writer.write_count(len(lod_controls))
        for lod_control in lod_controls:
            with writer.sub_block(TokenID.lod_control):
                with writer.sub_block(TokenID.distance_levels_header):
                    writer.write_int(lod_control.distance_levels_header)
                write_distance_levels(writer, lod_control.distance_levels)


def write_distance_levels(writer: BlockWriter, distance_levels: list) -> None:
    with writer.sub_block(TokenID.distance_levels):
        writer.write_count(len(distance_levels))
        for distance_level in distance_levels:
            with writer.sub_block(TokenID.distance_level):
                write_distance_level_header(writer, distance_level.distance_level_header)
                write_sub_objects(writer, distance_level.sub_objects)


def write_distance_level_header(writer: BlockWriter, header: DistanceLevelHeader) -> None:
    with writer.sub_block(TokenID.distance_level_header):
        with writer.sub_block(TokenID.dlevel_selection):
            writer.write_float(header.dlevel_selection)
        with writer.sub_block(TokenID.hierarchy):
            writer.write_count(len(header.hierarchy))
            for value in header.hierarchy:
                writer.write_int(value)


def write_sub_objects(writer: BlockWriter, sub_objects: list) -> None:
    with writer.sub_block(TokenID.sub_objects):
        writer.write_count(len(sub_objects))
        for sub_object in sub_objects:
            with writer.sub_block(TokenID.sub_object):
                write_sub_object_header(writer, sub_object.sub_object_header)
                write_vertices(writer, sub_object.vertices)
                write_vertex_sets(writer, sub_object.vertex_sets)
                write_primitives(writer, sub_object.primitives)


def write_sub_object_header(writer: BlockWriter, header: SubObjectHeader) -> None:
    with writer.sub_block(TokenID.sub_object_header):
        writer.write_flags(header.flags)
        writer.write_int(header.sort_vector_index)
        writer.write_int(header.volume_index)
        writer.write_flags(header.source_vtx_fmt_flags)
        writer.write_flags(header.destination_vtx_fmt_flags)
        write_geometry_info(writer, header.geometry_info)
        write_subobject_shaders(writer, header.subobject_shaders)
        write_subobject_light_cfgs(writer, header.subobject_light_cfgs)
        writer.write_int(header.subobject_id)


def write_geometry_info(writer: BlockWriter, info: GeometryInfo) -> None:
    with writer.sub_block(TokenID.geometry_info):
        writer.write_int(info.face_normals)
        writer.write_int(info.tx_light_cmds)
        writer.write_int(info.node_x_tx_light_cmds)
        writer.write_int(info.trilist_indices)
        writer.write_int(info.line_list_indices)
        writer.write_int(info.node_x_trilist_indices)
        writer.write_int(info.trilists)
        writer.write_int(info.line_lists)
        writer.write_int(info.pt_lists)
        writer.write_int(info.node_x_trilists)
        write_geometry_nodes(writer, info.geometry_nodes)
        write_geometry_node_map(writer, info.geometry_node_map)


def write_geometry_nodes(writer: BlockWriter, geometry_nodes: list) -> None:
    with writer.sub_block(TokenID.geometry_nodes):
        writer.write_count(len(geometry_nodes))
        for geometry_node in geometry_nodes:
            with writer.sub_block(TokenID.geometry_node):
                writer.write_int(geometry_node.tx_light_cmds)
                writer.write_int(geometry_node.node_x_tx_light_cmds)
                writer.write_int(geometry_node.trilists)
                writer.write_int(geometry_node.line_lists)
                writer.write_int(geometry_node.pt_lists)
                write_cullable_prims(writer, geometry_node.cullable_prims)


def write_cullable_prims(writer: BlockWriter, cullable_prims: CullablePrims) -> None:
    with writer.sub_block(TokenID.cullable_prims):
        writer.write_int(cullable_prims.num_prims)
        writer.write_int(cullable_prims.num_flat_sections)
        writer.write_int(cullable_prims.num_prim_indices)


def write_geometry_node_map(writer: BlockWriter, geometry_node_map: list) -> None:
    with writer.sub_block(TokenID.geometry_node_map):
        writer.write_count(len(geometry_node_map))
        for value in geometry_node_map:
            writer.write_int(value)


def write_subobject_shaders(writer: BlockWriter, shaders: list) -> None:
    with writer.sub_block(TokenID.subobject_shaders):
        writer.write_count(len(shaders))
        for shader in shaders:
            writer.write_int(shader)


def write_subobject_light_cfgs(writer: BlockWriter, light_cfgs: list) -> None:
    with writer.sub_block(TokenID.subobject_light_cfgs):
        writer.write_count(len(light_cfgs))
        for light_cfg in light_cfgs:
            writer.write_int(light_cfg)


def write_vertices(writer: BlockWriter, vertices: list) -> None:
    with writer.sub_block(TokenID.vertices):
        writer.write_count(len(vertices))
        for vertex in vertices:
            with writer.sub_block(TokenID.vertex):
                writer.write_flags(vertex.flags)
                writer.write_int(vertex.point_index)
                writer.write_int(vertex.normal_index)
                writer.write_flags(vertex.colour1)
                writer.write_flags(vertex.colour2)
                write_vertex_uvs(writer, vertex.vertex_uvs)


def write_vertex_uvs(writer: BlockWriter, vertex_uvs: list) -> None:
    with writer.sub_block(TokenID.vertex_uvs):
        writer.write_count(len(vertex_uvs))
        for vertex_uv in vertex_uvs:
            writer.write_int(vertex_uv)


def write_vertex_sets(writer: BlockWriter, vertex_sets: list) -> None:
    with writer.sub_block(TokenID.vertex_sets):
        writer.write_count(len(vertex_sets))
        for vertex_set in vertex_sets:
            with writer.sub_block(TokenID.vertex_set):
                writer.write_int(vertex_set.vtx_state)
                writer.write_int(vertex_set.vtx_start_index)
                writer.write_int(vertex_set.vtx_count)


def write_primitives(writer: BlockWriter, primitives: list) -> None:
    with writer.sub_block(TokenID.primitives):
        writer.write_count(len(primitives))
        for primitive in primitives:
            with writer.sub_block(TokenID.prim_state_idx):
                writer.write_int(primitive.prim_state_index)
            with writer.sub_block(TokenID.indexed_trilist):
                write_vertex_idxs(writer, primitive.indexed_trilist.vertex_idxs)
                write_normal_idxs(writer, primitive.indexed_trilist.normal_idxs)
                write_flags(writer, primitive.indexed_trilist.flags)


def write_vertex_idxs(writer: BlockWriter, vertex_idxs: list) -> None:
    with writer.sub_block(TokenID.vertex_idxs):
        writer.write_count(len(vertex_idxs) * 3)
        for vertex_idx in vertex_idxs:
            writer.write_int(vertex_idx.vertex1_index)
            writer.write_int(vertex_idx.vertex2_index)
            writer.write_int(vertex_idx.vertex3_index)


def write_normal_idxs(writer: BlockWriter, normal_idxs: list) -> None:
    with writer.sub_block(TokenID.normal_idxs):
        writer.write_count(len(normal_idxs))
        for normal_idx in normal_idxs:
            writer.write_int(normal_idx.index)
            writer.write_int(normal_idx.unknown2)


def write_flags(writer: BlockWriter, flags: list) -> None:
    with writer.sub_block(TokenID.flags):
        writer.write_count(len(flags))
        for flag in flags:
            writer.write_flags(flag)


def write_animations(writer: BlockWriter, animations: list) -> None:
    with writer.sub_block(TokenID.animations):
        writer.write_count(len(animations))
        for animation in animations:
            with writer.sub_block(TokenID.animation):
                writer.write_int(animation.frame_count)
                writer.write_int(animation.frame_rate)
                write_anim_nodes(writer, animation.animation_nodes)


def write_anim_nodes(writer: BlockWriter, anim_nodes: list) -> None:
    with writer.sub_block(TokenID.anim_nodes):
        writer.write_count(len(anim_nodes))
        for anim_node in anim_nodes:
            with writer.sub_block(TokenID.anim_node, label=anim_node.name):
                write_controllers(writer, anim_node.controllers)


def write_controllers(writer: BlockWriter, controllers: list) -> None:
    with writer.sub_block(TokenID.controllers):
        writer.write_count(len(controllers))
        for controller in controllers:
            if isinstance(controller, TCBRot):
                with writer.sub_block(TokenID.tcb_rot):
                    write_keypositions(writer, controller.keyframes)
            elif isinstance(controller, LinearPos):
                with writer.sub_block(TokenID.linear_pos):
                    write_keypositions(writer, controller.keyframes)
            elif isinstance(controller, TCBPos):
                with writer.sub_block(TokenID.tcb_pos):
                    write_keypositions(writer, controller.keyframes)


def write_keypositions(writer: BlockWriter, keypositions: list) -> None:
    writer.write_count(len(keypositions))
    for keyposition in keypositions:
        if isinstance(keyposition, TCBKey):
            with writer.sub_block(TokenID.tcb_key):
                writer.write_int(keyposition.frame)
                writer.write_float(keyposition.x)
                writer.write_float(keyposition.y)
                writer.write_float(keyposition.z)
                writer.write_float(keyposition.w)
                writer.write_float(keyposition.tension)
                writer.write_float(keyposition.continuity)
                writer.write_float(keyposition.bias)
                writer.write_float(keyposition.ease_in)
                writer.write_float(keyposition.ease_out)
        elif isinstance(keyposition, LinearKey):
            with writer.sub_block(TokenID.linear_key):
                writer.write_int(keyposition.frame)
                writer.write_float(keyposition.x)
                writer.write_float(keyposition.y)
                writer.write_float(keyposition.z)
        elif isinstance(keyposition, SlerpRot):
            with writer.sub_block(TokenID.slerp_rot):
                writer.write_int(keyposition.frame)
                writer.write_float(keyposition.x)
                writer.write_float(keyposition.y)
                writer.write_float(keyposition.z)
                writer.write_float(keyposition.w)