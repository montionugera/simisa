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

import logging
from typing import List

from .. import TokenID, Units
from ..reader import BlockReader, SimisaSubheaderError
from .models import *

logger = logging.getLogger(__name__)



def load(filepath: str) -> Shape:
    """
    Load and parse a shape file from disk.

    This function supports both compressed/uncompressed as well as binary/text data.
    It opens the file at the given path, validates that it is a supported shape
    file based on its subheader, and returns a parsed Shape object.

    Args:
        filepath (str): Path to the shape file.

    Returns:
        Shape: The parsed shape object.

    Raises:
        TypeError: If `filepath` is not a string.
        SimisaHeaderError: If the data has an invalid or unrecognized SIMISA header.
        SimisaSubheaderError: If the data has an invalid or unrecognized SIMISA subheader.
        BlockReaderError: If the block reader encounters an error or malformed data.
        StfReaderError: If the STF reader encounters an error or malformed data.
        OSError: If the file cannot be opened.
    """
    if not isinstance(filepath, str):
        raise TypeError(f"Parameter 'filepath' must be str, but got {type(filepath).__name__}")

    with BlockReader.open(filepath) as reader:

        if not reader.filetype == 's':
            raise SimisaSubheaderError(f"Unrecognized filetype '{reader.filetype}' in subheader. Is it a shape?")

        return read_shape(reader)


def loads(shape_text: str) -> Shape:
    """
    Parse a shape from a string containing shape data.

    This function does not support binary or compressed data. It reads shape
    data from the provided string, validates that it represents a supported
    shape file based on its subheader, and returns a parsed Shape object.

    Args:
        shape_text (str): String containing shape file data.

    Returns:
        Shape: The parsed shape object.

    Raises:
        TypeError: If `shape_text` is not a string.
        SimisaHeaderError: If the data has an invalid or unrecognized SIMISA header.
        SimisaSubheaderError: If the data has an invalid or unrecognized SIMISA subheader.
        BlockReaderError: If the block reader encounters an error or malformed data.
        StfReaderError: If the STF reader encounters an error or malformed data.
    """
    if not isinstance(shape_text, str):
        raise TypeError(f"Parameter 'shape_text' must be str, but got {type(shape_text).__name__}")

    reader = BlockReader.from_string(shape_text)

    if not reader.filetype == 's':
        raise SimisaSubheaderError(f"Unrecognized filetype '{reader.filetype}' in subheader. Is it a shape?")

    return read_shape(reader)


def read_shape(reader: BlockReader) -> Shape:
    """
    Read and parse a shape block from a BlockReader.

    Consumes the `shape` sub-block and its child sections, returning a fully
    constructed Shape object.

    Args:
        reader (BlockReader): Reader positioned at a shape block.

    Returns:
        Shape: The parsed shape.
    """
    with reader.sub_block(TokenID.shape) as shape_block:
        shape_header = read_shape_header(shape_block)
        volumes = read_volumes(shape_block)
        shader_names = read_shader_names(shape_block)
        texture_filter_names = read_texture_filter_names(shape_block)
        points = read_points(shape_block)
        uv_points = read_uv_points(shape_block)
        normals = read_normals(shape_block)
        sort_vectors = read_sort_vectors(shape_block)
        colours = read_colours(shape_block)
        matrices = read_matrices(shape_block)
        images = read_images(shape_block)
        textures = read_textures(shape_block)
        light_materials = read_light_materials(shape_block)
        light_model_cfgs = read_light_model_cfgs(shape_block)
        vtx_states = read_vtx_states(shape_block)
        prim_states = read_prim_states(shape_block)
        lod_controls: List[LodControl] = []
        animations: List[Animation] = []

        return Shape(
            shape_header,
            volumes,
            shader_names,
            texture_filter_names,
            points,
            uv_points,
            normals,
            sort_vectors,
            colours,
            matrices,
            images,
            textures,
            light_materials,
            light_model_cfgs,
            vtx_states,
            prim_states,
            lod_controls,
            animations,
        )


def read_shape_header(reader: BlockReader) -> ShapeHeader:
    """
    Read and parse a shape header block from a BlockReader.

    Consumes the `shape_header` sub-block and its child sections, returning a fully
    constructed ShapeHeader object.

    Args:
        reader (BlockReader): Reader positioned at a shape header block.

    Returns:
        ShapeHeader: The parsed shape header.
    """
    with reader.sub_block(TokenID.shape_header) as header_block:
        flags1 = header_block.read_flags()
        flags2 = None

        if not header_block.end_of_block():
            flags2 = header_block.read_flags()

        return ShapeHeader(flags1, flags2)


def read_volumes(reader: BlockReader) -> List[VolumeSphere]:
    """
    Read and parse volume spheres from a BlockReader.

    Consumes the `volumes` sub-block and returns a list of VolumeSphere objects.

    Args:
        reader (BlockReader): Reader positioned at a volumes block.

    Returns:
        List[VolumeSphere]: The parsed volume spheres.
    """
    with reader.sub_block(TokenID.volumes) as volumes_block:
        volume_spheres: List[VolumeSphere] = []
        count = volumes_block.read_int()
        
        for vol_sphere_block in volumes_block:
            vol_sphere_block.verify_id(TokenID.vol_sphere)

            vector = read_vector(vol_sphere_block)
            radius = vol_sphere_block.read_float()

            volume_spheres.append(VolumeSphere(radius, vector))

        volumes_block.verify_count(count, len(volume_spheres))

        return volume_spheres


def read_vector(reader: BlockReader) -> Vector:
    """
    Read and parse a 3D vector from a BlockReader.

    Consumes the `vector` sub-block and returns a Vector object.

    Args:
        reader (BlockReader): Reader positioned at a vector block.

    Returns:
        Vector: The parsed vector.
    """
    with reader.sub_block(TokenID.vector) as vector_block:
        x = vector_block.read_float()
        y = vector_block.read_float()
        z = vector_block.read_float()

        return Vector(x, y, z)


def read_shader_names(reader: BlockReader) -> List[str]:
    """
    Read and parse shader names from a BlockReader.

    Consumes the `shader_names` sub-block and returns a list of strings.

    Args:
        reader (BlockReader): Reader positioned at a shader names block.

    Returns:
        List[str]: The parsed shader names.
    """
    with reader.sub_block(TokenID.shader_names) as shader_names_block:
        shader_names: List[str] = []
        count = shader_names_block.read_int()
        
        for named_shader_block in shader_names_block:
            named_shader_block.verify_id(TokenID.named_shader)

            named_shader = named_shader_block.read_string()
            shader_names.append(named_shader)

        shader_names_block.verify_count(count, len(shader_names))

        return shader_names


def read_texture_filter_names(reader: BlockReader) -> List[str]:
    """
    Read and parse texture filter names from a BlockReader.

    Consumes the `texture_filter_names` sub-block and returns a list of strings.

    Args:
        reader (BlockReader): Reader positioned at a texture filter names block.

    Returns:
        List[str]: The parsed texture filter names.
    """
    with reader.sub_block(TokenID.texture_filter_names) as texture_filter_names_block:
        named_filter_modes: List[str] = []
        count = texture_filter_names_block.read_int()
        
        for named_filter_mode_block in texture_filter_names_block:
            named_filter_mode_block.verify_id(TokenID.named_filter_mode)

            named_filter_mode = named_filter_mode_block.read_string()
            named_filter_modes.append(named_filter_mode)

        texture_filter_names_block.verify_count(count, len(named_filter_modes))

        return named_filter_modes


def read_points(reader: BlockReader) -> List[Point]:
    """
    Read and parse 3D points from a BlockReader.

    Consumes the `points` sub-block and returns a list of Point objects.

    Args:
        reader (BlockReader): Reader positioned at a points block.

    Returns:
        List[Point]: The parsed points.
    """
    with reader.sub_block(TokenID.points) as points_block:
        points: List[Point] = []
        count = points_block.read_int()
        
        for point_block in points_block:
            point_block.verify_id(TokenID.point)

            x = point_block.read_float()
            y = point_block.read_float()
            z = point_block.read_float()

            points.append(Point(x, y, z))

        points_block.verify_count(count, len(points))

        return points


def read_uv_points(reader: BlockReader) -> List[UVPoint]:
    """
    Read and parse UV points from a BlockReader.

    Consumes the `uv_points` sub-block and returns a list of UVPoint objects.

    Args:
        reader (BlockReader): Reader positioned at a UV points block.

    Returns:
        List[UVPoint]: The parsed UV points.
    """
    with reader.sub_block(TokenID.uv_points) as uv_points_block:
        uv_points: List[UVPoint] = []
        count = uv_points_block.read_int()
        
        for uv_point_block in uv_points_block:
            uv_point_block.verify_id(TokenID.uv_point)

            u = uv_point_block.read_float()
            v = uv_point_block.read_float()

            uv_points.append(UVPoint(u, v))

        uv_points_block.verify_count(count, len(uv_points))

        return uv_points


def read_normals(reader: BlockReader) -> List[Vector]:
    """
    Read and parse normal vectors from a BlockReader.

    Consumes the `normals` sub-block and returns a list of Vector objects.

    Args:
        reader (BlockReader): Reader positioned at a normals block.

    Returns:
        List[Vector]: The parsed normals.
    """
    with reader.sub_block(TokenID.normals) as normals_block:
        normals: List[Vector] = []
        count = normals_block.read_int()
        
        for vector_block in normals_block:
            vector_block.verify_id(TokenID.vector)

            x = vector_block.read_float()
            y = vector_block.read_float()
            z = vector_block.read_float()

            normals.append(Vector(x, y, z))

        normals_block.verify_count(count, len(normals))

        return normals



def read_sort_vectors(reader: BlockReader) -> List[Vector]:
    """
    Read and parse sort vectors from a BlockReader.

    Consumes the `sort_vectors` sub-block and returns a list of Vector objects.

    Args:
        reader (BlockReader): Reader positioned at a sort vectors block.

    Returns:
        List[Vector]: The parsed sort vectors.
    """
    with reader.sub_block(TokenID.sort_vectors) as sort_vectors_block:
        sort_vectors: List[Vector] = []
        count = sort_vectors_block.read_int()
        
        for vector_block in sort_vectors_block:
            vector_block.verify_id(TokenID.vector)

            x = vector_block.read_float()
            y = vector_block.read_float()
            z = vector_block.read_float()

            sort_vectors.append(Vector(x, y, z))

        sort_vectors_block.verify_count(count, len(sort_vectors))

        return sort_vectors


def read_colours(reader: BlockReader) -> List[Colour]:
    """
    Read and parse colours from a BlockReader.

    Consumes the `colours` sub-block and returns a list of Colour objects.

    Args:
        reader (BlockReader): Reader positioned at a colours block.

    Returns:
        List[Colour]: The parsed colours.
    """
    with reader.sub_block(TokenID.colours) as colours_block:
        colours: List[Colour] = []
        count = colours_block.read_int()
        
        for colour_block in colours_block:
            colour_block.verify_id(TokenID.colour)

            a = colour_block.read_float()
            r = colour_block.read_float()
            g = colour_block.read_float()
            b = colour_block.read_float()

            colours.append(Colour(a, r, g, b))

        colours_block.verify_count(count, len(colours))

        return colours


def read_matrices(reader: BlockReader) -> List[Matrix]:
    """
    Read and parse transformation matrices from a BlockReader.

    Consumes the `matrices` sub-block and returns a list of Matrix objects.

    Args:
        reader (BlockReader): Reader positioned at a matrices block.

    Returns:
        List[Matrix]: The parsed matrices.
    """
    with reader.sub_block(TokenID.matrices) as matrices_block:
        matrices: List[Matrix] = []
        count = matrices_block.read_int()
        
        for matrix_block in matrices_block:
            matrix_block.verify_id(TokenID.matrix)

            name = matrix_block.label
            ax = matrix_block.read_float()
            ay = matrix_block.read_float()
            az = matrix_block.read_float()
            bx = matrix_block.read_float()
            by = matrix_block.read_float()
            bz = matrix_block.read_float()
            cx = matrix_block.read_float()
            cy = matrix_block.read_float()
            cz = matrix_block.read_float()
            dx = matrix_block.read_float()
            dy = matrix_block.read_float()
            dz = matrix_block.read_float()

            matrix = Matrix(
                name,
                ax, ay, az,
                bx, by, bz,
                cx, cy, cz,
                dx, dy, dz
            )
            matrices.append(matrix)

        matrices_block.verify_count(count, len(matrices))

        return matrices


def read_images(reader: BlockReader) -> List[str]:
    """
    Read and parse image names from a BlockReader.

    Consumes the `images` sub-block and returns a list of strings.

    Args:
        reader (BlockReader): Reader positioned at an images block.

    Returns:
        List[str]: The parsed image names.
    """
    with reader.sub_block(TokenID.images) as images_block:
        images: List[str] = []
        count = images_block.read_int()
        
        for image_block in images_block:
            image_block.verify_id(TokenID.image)

            image = image_block.read_string()
            images.append(image)

        images_block.verify_count(count, len(images))

        return images


def read_textures(reader: BlockReader) -> List[Texture]:
    """
    Read and parse textures from a BlockReader.

    Consumes the `textures` sub-block and returns a list of Texture objects.

    Args:
        reader (BlockReader): Reader positioned at a textures block.

    Returns:
        List[Texture]: The parsed textures.
    """
    with reader.sub_block(TokenID.textures) as textures_block:
        textures: List[Texture] = []
        count = textures_block.read_int()
        
        for texture_block in textures_block:
            texture_block.verify_id(TokenID.texture)

            image_index = texture_block.read_int()
            filter_mode = texture_block.read_int()
            mipmap_lod_bias = texture_block.read_float()
            border_colour = None
            
            if not texture_block.end_of_block():
                border_colour = texture_block.read_flags()
            
            texture = Texture(
                image_index,
                filter_mode,
                mipmap_lod_bias,
                border_colour
            )
            textures.append(texture)

        textures_block.verify_count(count, len(textures))

        return textures


def read_light_materials(reader: BlockReader) -> List[LightMaterial]:
    """
    Read and parse light materials from a BlockReader.

    Consumes the `light_materials` sub-block and returns a list of LightMaterial objects.

    Args:
        reader (BlockReader): Reader positioned at a light materials block.

    Returns:
        List[LightMaterial]: The parsed light materials.
    """
    with reader.sub_block(TokenID.light_materials) as light_materials_block:
        light_materials: List[LightMaterial] = []
        count = light_materials_block.read_int()

        for light_material_block in light_materials_block:
            light_material_block.verify_id(TokenID.light_material)

            flags = light_material_block.read_flags()
            diff_colour_index = light_material_block.read_int()
            amb_colour_index = light_material_block.read_int()
            spec_colour_index = light_material_block.read_int()
            emissive_colour_index = light_material_block.read_int()
            spec_power = light_material_block.read_float()

            light_material = LightMaterial(
                flags,
                diff_colour_index,
                amb_colour_index,
                spec_colour_index,
                emissive_colour_index,
                spec_power
            )
            light_materials.append(light_material)

        light_materials_block.verify_count(count, len(light_materials))

        return light_materials


def read_light_model_cfgs(reader: BlockReader) -> List[LightModelCfg]:
    """
    Read and parse light model configurations from a BlockReader.

    Consumes the `light_model_cfgs` sub-block and returns a list of LightModelCfg objects.

    Args:
        reader (BlockReader): Reader positioned at a light model configs block.

    Returns:
        List[LightModelCfg]: The parsed light model configurations.
    """
    with reader.sub_block(TokenID.light_model_cfgs) as light_model_cfgs_block:
        light_model_cfgs: List[LightMaterial] = []
        count = light_model_cfgs_block.read_int()

        for light_model_cfg_block in light_model_cfgs_block:
            light_model_cfg_block.verify_id(TokenID.light_model_cfg)

            flags = light_model_cfg_block.read_flags()
            uv_ops = read_uv_ops(light_model_cfg_block)

            light_model_cfgs.append(LightModelCfg(flags, uv_ops))

        light_model_cfgs_block.verify_count(count, len(light_model_cfgs))

        return light_model_cfgs


def read_uv_ops(reader: BlockReader) -> List[UVOp]:
    """
    Read and parse UV operations from a BlockReader.

    Consumes the `uv_ops` sub-block and returns a list of UVOp objects.

    Args:
        reader (BlockReader): Reader positioned at a UV ops block.

    Returns:
        List[UVOp]: The parsed UV operations.
    """
    with reader.sub_block(TokenID.uv_ops) as uv_ops_block:
        count = uv_ops_block.read_int()
        uv_ops: List[UVOp] = []

        for uv_op_block in uv_ops_block:
            if uv_op_block.id == TokenID.uv_op_copy:
                texture_address_mode = uv_op_block.read_int()
                source_uv_index = uv_op_block.read_int()

                uv_ops.append(UVOpCopy(
                    texture_address_mode,
                    source_uv_index
                ))

            elif uv_op_block.id == TokenID.uv_op_reflectmapfull:
                texture_address_mode = uv_op_block.read_int()

                uv_ops.append(UVOpReflectMapFull(
                    texture_address_mode
                ))

            elif uv_op_block.id == TokenID.uv_op_reflectmap:
                texture_address_mode = uv_op_block.read_int()

                uv_ops.append(UVOpReflectMap(
                    texture_address_mode
                ))

            elif uv_op_block.id == TokenID.uv_op_uniformscale:
                texture_address_mode = uv_op_block.read_int()
                source_uv_index = uv_op_block.read_int()
                unknown3 = uv_op_block.read_int()
                unknown4 = uv_op_block.read_int()

                uv_ops.append(UVOpUniformScale(
                    texture_address_mode,
                    source_uv_index,
                    unknown3,
                    unknown4
                ))

            elif uv_op_block.id == TokenID.uv_op_nonuniformscale:
                texture_address_mode = uv_op_block.read_int()
                source_uv_index = uv_op_block.read_int()
                unknown3 = uv_op_block.read_int()
                unknown4 = uv_op_block.read_int()

                uv_ops.append(UVOpNonUniformScale(
                    texture_address_mode,
                    source_uv_index,
                    unknown3,
                    unknown4
                ))

            else:
                logger.warning(f"Unhandled uv_op: {uv_op_block.id.name} (id: {uv_op_block.id})")
        
        uv_ops_block.verify_count(count, len(uv_ops))

        return uv_ops


def read_vtx_states(reader: BlockReader) -> List[VtxState]:
    """
    Read and parse vertex states from a BlockReader.

    Consumes the `vtx_states` sub-block and returns a list of VtxState objects.

    Args:
        reader (BlockReader): Reader positioned at a vertex states block.

    Returns:
        List[VtxState]: The parsed vertex states.
    """
    with reader.sub_block(TokenID.vtx_states) as vtx_states_block:
        vtx_states: List[VtxState] = []
        count = vtx_states_block.read_int()
        
        for vtx_state_block in vtx_states_block:
            vtx_state_block.verify_id(TokenID.vtx_state)

            flags = vtx_state_block.read_flags()
            matrix_index = vtx_state_block.read_int()
            light_material_index = vtx_state_block.read_int()
            light_model_cfg_index = vtx_state_block.read_int()
            light_flags = vtx_state_block.read_flags()
            matrix2_index = None
            
            if not vtx_state_block.end_of_block():
                matrix2_index = vtx_state_block.read_int()
            
            vtx_state = VtxState(
                flags,
                matrix_index,
                light_material_index,
                light_model_cfg_index,
                light_flags,
                matrix2_index
            )
            vtx_states.append(vtx_state)

        vtx_states_block.verify_count(count, len(vtx_states))

        return vtx_states


def read_prim_states(reader: BlockReader) -> List[PrimState]:
    """
    Read and parse primitive states from a BlockReader.

    Consumes the `prim_states` sub-block and returns a list of PrimState objects.

    Args:
        reader (BlockReader): Reader positioned at a primitive states block.

    Returns:
        List[PrimState]: The parsed primitive states.
    """
    with reader.sub_block(TokenID.prim_states) as prim_states_block:
        prim_states: List[VtxState] = []
        count = prim_states_block.read_int()
        
        for prim_state_block in prim_states_block:
            prim_state_block.verify_id(TokenID.prim_state)

            name = prim_state_block.label
            flags = prim_state_block.read_flags()
            shader_index = prim_state_block.read_int()
            texture_indices = read_tex_idxs(prim_state_block)
            z_bias = prim_state_block.read_float()
            vtx_state_index = prim_state_block.read_int()
            alpha_test_mode = prim_state_block.read_int()
            light_cfg_index = prim_state_block.read_int()
            z_buffer_mode = prim_state_block.read_int()
            
            prim_state = PrimState(
                name,
                flags,
                shader_index,
                texture_indices,
                z_bias,
                vtx_state_index,
                alpha_test_mode,
                light_cfg_index,
                z_buffer_mode
            )
            prim_states.append(prim_state)

        prim_states_block.verify_count(count, len(prim_states))

        return prim_states


def read_tex_idxs(reader: BlockReader) -> List[int]:
    """
    Read and parse texture index lists from a BlockReader.

    Consumes the `tex_idxs` sub-block and returns a list of integer texture indices.

    Args:
        reader (BlockReader): Reader positioned at a texture indices block.

    Returns:
        List[int]: The parsed texture indices.
    """
    with reader.sub_block(TokenID.tex_idxs) as tex_idxs_block:
        tex_idxs: List[int] = []
        count = tex_idxs_block.read_int()
        
        for _ in range(count):
            tex_idxs.append(tex_idxs_block.read_int())

        tex_idxs_block.verify_count(count, len(tex_idxs))

        return tex_idxs