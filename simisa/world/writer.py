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
from ..tracksections.writer import write_local_tracksections
from .models import *


def dump(world: World, filepath: str, compressed: bool = False) -> None:
    """
    Write a world object to disk.

    This function supports both compressed/uncompressed as well as binary/text data.
    It writes the world data to the file at the given path.

    Args:
        world (World): The world object to write.
        filepath (str): Path to the output file.
        compressed (bool): Whether to write compressed data. Defaults to False.

    Raises:
        TypeError: If `world` is not a World object.
        TypeError: If `filepath` is not a string.
        TypeError: If `compressed` is not a bool.
        OSError: If the file cannot be written.
    """
    if not isinstance(world, World):
        raise TypeError(f"Parameter 'world' must be World, but got {type(world).__name__}")

    if not isinstance(filepath, str):
        raise TypeError(f"Parameter 'filepath' must be str, but got {type(filepath).__name__}")

    if not isinstance(compressed, bool):
        raise TypeError(f"Parameter 'compressed' must be bool, but got {type(compressed).__name__}")

    with BlockWriter.open(
        filepath,
        filetype="w",
        fileversion="0",
        is_binary=compressed,
        is_unicode=not compressed,
        is_compressed=compressed
    ) as writer:
        write_world(writer, world)


def dumps(world: World) -> str:
    """
    Write a world object to a string.

    This function does not support binary or compressed data. It writes world
    data to a string and returns it.

    Args:
        world (World): The world object to write.

    Returns:
        str: The string containing the world data.

    Raises:
        TypeError: If `world` is not a World object.
    """
    if not isinstance(world, World):
        raise TypeError(f"Parameter 'world' must be World, but got {type(world).__name__}")

    world_text = BlockWriter.to_string(
        lambda writer: write_world(writer, world),
        filetype="w",
        fileversion="0"
    )

    return world_text


def write_world(writer: BlockWriter, world: World) -> None:
    """
    Write a world block to a BlockWriter.

    Writes the `Tr_Worldfile` sub-block and its child blocks.

    Args:
        writer (BlockWriter): Writer to write the world block to.
        world (World): The world object to write.
    """
    with writer.sub_block(TokenID.Tr_Worldfile):
        write_world_objects(writer, world.objects)


def write_world_objects(writer: BlockWriter, objects: list) -> None:
    """
    Write world objects to a BlockWriter.

    Writes world objects by dispatching to the appropriate object type writer.

    Args:
        writer (BlockWriter): Writer to write the world objects to.
        objects (list): List of world object objects to write.
    """
    current_watermark = 0

    for obj in objects:
        if isinstance(obj, StaticObj):
            write_static_object(writer, obj, current_watermark)
        elif isinstance(obj, TrackObj):
            write_track_object(writer, obj, current_watermark)
        elif isinstance(obj, CarSpawnerObj):
            write_carspawner_object(writer, obj, current_watermark)
        elif isinstance(obj, SidingObj):
            write_siding_object(writer, obj, current_watermark)
        elif isinstance(obj, PlatformObj):
            write_platform_object(writer, obj, current_watermark)
        elif isinstance(obj, ForestObj):
            write_forest_object(writer, obj, current_watermark)
        elif isinstance(obj, LevelCrObj):
            write_levelcr_object(writer, obj, current_watermark)
        elif isinstance(obj, DynTrackObj):
            write_dyntrack_object(writer, obj, current_watermark)
        elif isinstance(obj, TransferObj):
            write_transfer_object(writer, obj, current_watermark)
        elif isinstance(obj, GantryObj):
            write_gantry_object(writer, obj, current_watermark)
        elif isinstance(obj, PickupObj):
            write_pickup_object(writer, obj, current_watermark)
        elif isinstance(obj, HazardObj):
            write_hazard_object(writer, obj, current_watermark)
        elif isinstance(obj, SignalObj):
            write_signal_object(writer, obj, current_watermark)
        elif isinstance(obj, SpeedPostObj):
            write_speedpost_object(writer, obj, current_watermark)


def write_static_object(writer: BlockWriter, obj: StaticObj, detail_level: int) -> None:
    """
    Write a static object to a BlockWriter.

    Writes the `Static` sub-block and its child blocks.

    Args:
        writer (BlockWriter): Writer to write the static object to.
        obj (StaticObj): The static object to write.
        detail_level (int): Detail level associated with the object.
    """
    with writer.sub_block(TokenID.Static):
        write_world_obj_base(writer, obj, detail_level)


def write_track_object(writer: BlockWriter, obj: TrackObj, detail_level: int) -> None:
    """
    Write a track object to a BlockWriter.

    Writes the `TrackObj` sub-block and its child blocks.

    Args:
        writer (BlockWriter): Writer to write the track object to.
        obj (TrackObj): The track object to write.
        detail_level (int): Detail level associated with the object.
    """
    with writer.sub_block(TokenID.TrackObj):
        write_world_obj_base(writer, obj, detail_level)
        with writer.sub_block(TokenID.SectionIdx):
            writer.write_uint(obj.section_index)
        with writer.sub_block(TokenID.Elevation):
            writer.write_float(obj.elevation)
        with writer.sub_block(TokenID.CollideFlags):
            writer.write_flags(obj.collide_flags)
        if obj.jnode_position is not None:
            write_jnode_position(writer, obj.jnode_position)


def write_carspawner_object(writer: BlockWriter, obj: CarSpawnerObj, detail_level: int) -> None:
    """
    Write a car spawner object to a BlockWriter.

    Writes the `CarSpawner` sub-block and its child blocks.

    Args:
        writer (BlockWriter): Writer to write the car spawner object to.
        obj (CarSpawnerObj): The car spawner object to write.
        detail_level (int): Detail level associated with the object.
    """
    with writer.sub_block(TokenID.CarSpawner):
        write_world_obj_base(writer, obj, detail_level)
        with writer.sub_block(TokenID.CarFrequency):
            writer.write_float(obj.car_frequency)
        with writer.sub_block(TokenID.CarAvSpeed):
            writer.write_float(obj.car_avg_speed)
        if obj.list_name is not None:
            with writer.sub_block(TokenID.ORTSListName):
                writer.write_string(obj.list_name)
        if obj.tr_item_ids:
            for tr_item_id in obj.tr_item_ids:
                write_tr_item_id(writer, tr_item_id)


def write_siding_object(writer: BlockWriter, obj: SidingObj, detail_level: int) -> None:
    """
    Write a siding object to a BlockWriter.

    Writes the `Siding` sub-block and its child blocks.

    Args:
        writer (BlockWriter): Writer to write the siding object to.
        obj (SidingObj): The siding object to write.
        detail_level (int): Detail level associated with the object.
    """
    with writer.sub_block(TokenID.Siding):
        write_world_obj_base(writer, obj, detail_level)
        if obj.tr_item_ids:
            for tr_item_id in obj.tr_item_ids:
                write_tr_item_id(writer, tr_item_id)


def write_platform_object(writer: BlockWriter, obj: PlatformObj, detail_level: int) -> None:
    """
    Write a platform object to a BlockWriter.

    Writes the `Platform` sub-block and its child blocks.

    Args:
        writer (BlockWriter): Writer to write the platform object to.
        obj (PlatformObj): The platform object to write.
        detail_level (int): Detail level associated with the object.
    """
    with writer.sub_block(TokenID.Platform):
        write_world_obj_base(writer, obj, detail_level)
        with writer.sub_block(TokenID.PlatformData):
            writer.write_flags(obj.platform_data)
        if obj.tr_item_ids:
            for tr_item_id in obj.tr_item_ids:
                write_tr_item_id(writer, tr_item_id)


def write_forest_object(writer: BlockWriter, obj: ForestObj, detail_level: int) -> None:
    """
    Write a forest object to a BlockWriter.

    Writes the `Forest` sub-block and its child blocks.

    Args:
        writer (BlockWriter): Writer to write the forest object to.
        obj (ForestObj): The forest object to write.
        detail_level (int): Detail level associated with the object.
    """
    with writer.sub_block(TokenID.Forest):
        write_world_obj_base(writer, obj, detail_level)
        if obj.tree_texture is not None:
            with writer.sub_block(TokenID.TreeTexture):
                writer.write_string(obj.tree_texture)
        if obj.scale_range is not None:
            with writer.sub_block(TokenID.ScaleRange):
                writer.write_float(obj.scale_range.minimum)
                writer.write_float(obj.scale_range.maximum)
        if obj.forest_area is not None:
            with writer.sub_block(TokenID.Area):
                writer.write_float(obj.forest_area.x)
                writer.write_float(obj.forest_area.z)
        if obj.population is not None:
            with writer.sub_block(TokenID.Population):
                writer.write_int(obj.population)
        if obj.tree_size is not None:
            with writer.sub_block(TokenID.TreeSize):
                writer.write_float(obj.tree_size.width)
                writer.write_float(obj.tree_size.height)


def write_levelcr_object(writer: BlockWriter, obj: LevelCrObj, detail_level: int) -> None:
    """
    Write a level crossing object to a BlockWriter.

    Writes the `LevelCr` sub-block and its child blocks.

    Args:
        writer (BlockWriter): Writer to write the level crossing object to.
        obj (LevelCrObj): The level crossing object to write.
        detail_level (int): Detail level associated with the object.
    """
    with writer.sub_block(TokenID.LevelCr):
        write_world_obj_base(writer, obj, detail_level)
        if obj.levelcr_params is not None:
            with writer.sub_block(TokenID.LevelCrParameters):
                writer.write_float(obj.levelcr_params.warning_time)
                writer.write_float(obj.levelcr_params.minimum_distance)
        if obj.crash_probability is not None:
            with writer.sub_block(TokenID.CrashProbability):
                writer.write_int(obj.crash_probability)
        if obj.levelcr_data is not None:
            with writer.sub_block(TokenID.LevelCrData):
                writer.write_flags(obj.levelcr_data.data1)
                writer.write_flags(obj.levelcr_data.data2)
        if obj.levelcr_timing is not None:
            with writer.sub_block(TokenID.LevelCrTiming):
                writer.write_float(obj.levelcr_timing.initial_timing)
                writer.write_float(obj.levelcr_timing.serious_timing)
                writer.write_float(obj.levelcr_timing.animation_timing)
        if obj.sound_filename:
            with writer.sub_block(TokenID.ORTSSoundFileName):
                writer.write_string(obj.sound_filename)
        if obj.tr_item_ids:
            for tr_item_id in obj.tr_item_ids:
                write_tr_item_id(writer, tr_item_id)


def write_dyntrack_object(writer: BlockWriter, obj: DynTrackObj, detail_level: int) -> None:
    """
    Write a dynamic track object to a BlockWriter.

    Writes the `Dyntrack` sub-block and its child blocks.

    Args:
        writer (BlockWriter): Writer to write the dynamic track object to.
        obj (DynTrackObj): The dynamic track object to write.
        detail_level (int): Detail level associated with the object.
    """
    with writer.sub_block(TokenID.Dyntrack):
        with writer.sub_block(TokenID.UiD):
            writer.write_uint(obj.uid)
        write_position(writer, obj.position)
        write_qdirection(writer, obj.direction)
        with writer.sub_block(TokenID.VDbId):
            writer.write_uint(obj.vdb_id)
        with writer.sub_block(TokenID.StaticFlags):
            writer.write_flags(obj.static_flags)
        with writer.sub_block(TokenID.SectionIdx):
            writer.write_uint(obj.section_index)
        with writer.sub_block(TokenID.Elevation):
            writer.write_float(obj.elevation)
        with writer.sub_block(TokenID.CollideFlags):
            writer.write_uint(obj.collide_flags)
        if obj.track_sections is not None:
            with writer.sub_block(TokenID.TrackSections):
                write_local_tracksections(writer, obj.track_sections)


def write_transfer_object(writer: BlockWriter, obj: TransferObj, detail_level: int) -> None:
    """
    Write a transfer object to a BlockWriter.

    Writes the `Transfer` sub-block and its child blocks.

    Args:
        writer (BlockWriter): Writer to write the transfer object to.
        obj (TransferObj): The transfer object to write.
        detail_level (int): Detail level associated with the object.
    """
    with writer.sub_block(TokenID.Transfer):
        write_world_obj_base(writer, obj, detail_level)
        with writer.sub_block(TokenID.Width):
            writer.write_float(obj.width)
        with writer.sub_block(TokenID.Height):
            writer.write_float(obj.height)


def write_gantry_object(writer: BlockWriter, obj: GantryObj, detail_level: int) -> None:
    """
    Write a gantry object to a BlockWriter.

    Writes the `Gantry` sub-block and its child blocks.

    Args:
        writer (BlockWriter): Writer to write the gantry object to.
        obj (GantryObj): The gantry object to write.
        detail_level (int): Detail level associated with the object.
    """
    with writer.sub_block(TokenID.Gantry):
        write_world_obj_base(writer, obj, detail_level)


def write_pickup_object(writer: BlockWriter, obj: PickupObj, detail_level: int) -> None:
    """
    Write a pickup object to a BlockWriter.

    Writes the `Pickup` sub-block and its child blocks.

    Args:
        writer (BlockWriter): Writer to write the pickup object to.
        obj (PickupObj): The pickup object to write.
        detail_level (int): Detail level associated with the object.
    """
    with writer.sub_block(TokenID.Pickup):
        write_world_obj_base(writer, obj, detail_level)
        if obj.speed_range is not None:
            with writer.sub_block(TokenID.SpeedRange):
                writer.write_float(obj.speed_range.min_mps)
                writer.write_float(obj.speed_range.max_mps)
        with writer.sub_block(TokenID.PickupType):
            writer.write_uint(obj.pickup_type)
            writer.write_uint(obj.unknown)
        if obj.max_stacked_containers is not None:
            with writer.sub_block(TokenID.ORTSMaxStackedContainers):
                writer.write_int(obj.max_stacked_containers)
        if obj.stack_locations_length is not None:
            with writer.sub_block(TokenID.ORTSStackLocationsLength):
                writer.write_float(obj.stack_locations_length)
        if obj.stack_locations:
            write_stack_locations(writer, obj.stack_locations)
        with writer.sub_block(TokenID.ORTSPickingSurfaceYOffset):
            writer.write_float(obj.picking_surface_y_offset)
        if obj.picking_surface_relative_top_start_position is not None:
            with writer.sub_block(TokenID.ORTSPickingSurfaceRelativeTopStartPosition):
                writer.write_float(obj.picking_surface_relative_top_start_position.x)
                writer.write_float(obj.picking_surface_relative_top_start_position.y)
                writer.write_float(obj.picking_surface_relative_top_start_position.z)
        with writer.sub_block(TokenID.ORTSGrabberArmsParts):
            writer.write_int(obj.grabber_arms_parts)
        if obj.crane_sound is not None:
            with writer.sub_block(TokenID.ORTSCraneSound):
                writer.write_string(obj.crane_sound)
        if obj.pickup_anim_data is not None:
            with writer.sub_block(TokenID.PickupAnimData):
                writer.write_float(obj.pickup_anim_data.pickup_options)
                writer.write_float(obj.pickup_anim_data.animation_speed)
        if obj.pickup_capacity is not None:
            with writer.sub_block(TokenID.PickupCapacity):
                writer.write_float(obj.pickup_capacity.quantity_available_kg * 2.20462)
                writer.write_float(obj.pickup_capacity.feed_rate_kg_per_s * 2.20462)
        if obj.tr_item_ids:
            for tr_item_id in obj.tr_item_ids:
                write_tr_item_id(writer, tr_item_id)


def write_stack_locations(writer: BlockWriter, stack_locations: list) -> None:
    """
    Write stack locations to a BlockWriter.

    Writes the `ORTSStackLocations` sub-block and its child blocks.

    Args:
        writer (BlockWriter): Writer to write the stack locations block to.
        stack_locations (list): List of stack location objects to write.
    """
    with writer.sub_block(TokenID.ORTSStackLocations):
        writer.write_count(len(stack_locations))
        for stack_location in stack_locations:
            with writer.sub_block(TokenID.StackLocation):
                if stack_location.position is not None:
                    write_position(writer, stack_location.position)
                with writer.sub_block(TokenID.MaxStackedContainers):
                    writer.write_int(stack_location.max_stacked_containers)
                with writer.sub_block(TokenID.Length):
                    writer.write_float(stack_location.length)
                if stack_location.flipped:
                    with writer.sub_block(TokenID.Flipped):
                        writer.write_int(1)


def write_hazard_object(writer: BlockWriter, obj: HazardObj, detail_level: int) -> None:
    """
    Write a hazard object to a BlockWriter.

    Writes the `Hazard` sub-block and its child blocks.

    Args:
        writer (BlockWriter): Writer to write the hazard object to.
        obj (HazardObj): The hazard object to write.
        detail_level (int): Detail level associated with the object.
    """
    with writer.sub_block(TokenID.Hazard):
        write_world_obj_base(writer, obj, detail_level)
        if obj.tr_item_id is not None:
            write_tr_item_id(writer, obj.tr_item_id)


def write_signal_object(writer: BlockWriter, obj: SignalObj, detail_level: int) -> None:
    """
    Write a signal object to a BlockWriter.

    Writes the `Signal` sub-block and its child blocks.

    Args:
        writer (BlockWriter): Writer to write the signal object to.
        obj (SignalObj): The signal object to write.
        detail_level (int): Detail level associated with the object.
    """
    with writer.sub_block(TokenID.Signal):
        write_world_obj_base(writer, obj, detail_level)
        with writer.sub_block(TokenID.SignalSubObj):
            writer.write_flags(obj.signal_sub_obj)
        if obj.signal_units:
            write_signal_units(writer, obj.signal_units)


def write_signal_units(writer: BlockWriter, signal_units: list) -> None:
    """
    Write signal units to a BlockWriter.

    Writes the `SignalUnits` sub-block and its child blocks.

    Args:
        writer (BlockWriter): Writer to write the signal units block to.
        signal_units (list): List of signal unit objects to write.
    """
    with writer.sub_block(TokenID.SignalUnits):
        writer.write_count(len(signal_units))
        for signal_unit in signal_units:
            with writer.sub_block(TokenID.SignalUnit):
                writer.write_int(signal_unit.sub_obj)
                with writer.sub_block(TokenID.TrItemId):
                    write_tr_item_id(writer, signal_unit.tr_item_id)


def write_speedpost_object(writer: BlockWriter, obj: SpeedPostObj, detail_level: int) -> None:
    """
    Write a speed post object to a BlockWriter.

    Writes the `Speedpost` sub-block and its child blocks.

    Args:
        writer (BlockWriter): Writer to write the speed post object to.
        obj (SpeedPostObj): The speed post object to write.
        detail_level (int): Detail level associated with the object.
    """
    with writer.sub_block(TokenID.Speedpost):
        write_world_obj_base(writer, obj, detail_level)
        if obj.speed_digit_tex is not None:
            with writer.sub_block(TokenID.Speed_Digit_Tex):
                writer.write_string(obj.speed_digit_tex)
        if obj.sign_shape is not None:
            with writer.sub_block(TokenID.Speed_Sign_Shape):
                writer.write_int(obj.sign_shape.num_shapes)
                for value in obj.sign_shape.shape_info:
                    writer.write_float(value)
        if obj.text_size is not None:
            with writer.sub_block(TokenID.Speed_Text_Size):
                writer.write_float(obj.text_size.size)
                writer.write_float(obj.text_size.dx)
                writer.write_float(obj.text_size.dy)
        if obj.tr_item_ids:
            for tr_item_id in obj.tr_item_ids:
                write_tr_item_id(writer, tr_item_id)


def write_world_obj_base(writer: BlockWriter, obj: WorldObj, detail_level: int) -> None:
    """
    Write the base fields of a world object to a BlockWriter.

    Writes the common sub-blocks shared by all world object types.

    Args:
        writer (BlockWriter): Writer to write the world object base to.
        obj (WorldObj): The world object to write.
        detail_level (int): Detail level associated with the object.
    """
    with writer.sub_block(TokenID.UiD):
        writer.write_uint(obj.uid)
    if obj.file_name is not None:
        with writer.sub_block(TokenID.FileName):
            writer.write_string(obj.file_name)
    write_position(writer, obj.position)
    write_qdirection(writer, obj.direction)
    if obj.matrix3x3 is not None:
        write_matrix3x3(writer, obj.matrix3x3)
    if obj.vdb_id is not None:
        with writer.sub_block(TokenID.VDbId):
            writer.write_uint(obj.vdb_id)
    with writer.sub_block(TokenID.StaticFlags):
        writer.write_flags(obj.static_flags)


def write_position(writer: BlockWriter, position: Position) -> None:
    """
    Write a position to a BlockWriter.

    Writes the `Position` sub-block.

    Args:
        writer (BlockWriter): Writer to write the position block to.
        position (Position): The position object to write.
    """
    with writer.sub_block(TokenID.Position):
        writer.write_float(position.x)
        writer.write_float(position.y)
        writer.write_float(position.z)


def write_qdirection(writer: BlockWriter, qdirection: QDirection) -> None:
    """
    Write a quaternion direction to a BlockWriter.

    Writes the `QDirection` sub-block.

    Args:
        writer (BlockWriter): Writer to write the quaternion direction block to.
        qdirection (QDirection): The quaternion direction object to write.
    """
    with writer.sub_block(TokenID.QDirection):
        writer.write_float(qdirection.x)
        writer.write_float(qdirection.y)
        writer.write_float(qdirection.z)
        writer.write_float(qdirection.w)


def write_matrix3x3(writer: BlockWriter, matrix3x3: Matrix3x3) -> None:
    """
    Write a 3x3 matrix to a BlockWriter.

    Writes the `Matrix3x3` sub-block.

    Args:
        writer (BlockWriter): Writer to write the 3x3 matrix block to.
        matrix3x3 (Matrix3x3): The 3x3 matrix object to write.
    """
    with writer.sub_block(TokenID.Matrix3x3):
        writer.write_float(matrix3x3.ax)
        writer.write_float(matrix3x3.ay)
        writer.write_float(matrix3x3.az)
        writer.write_float(matrix3x3.bx)
        writer.write_float(matrix3x3.by)
        writer.write_float(matrix3x3.bz)
        writer.write_float(matrix3x3.cx)
        writer.write_float(matrix3x3.cy)
        writer.write_float(matrix3x3.cz)


def write_jnode_position(writer: BlockWriter, jnode_position: JNodePosition) -> None:
    """
    Write a junction node position to a BlockWriter.

    Writes the `JNodePosn` sub-block.

    Args:
        writer (BlockWriter): Writer to write the junction node position block to.
        jnode_position (JNodePosition): The junction node position object to write.
    """
    with writer.sub_block(TokenID.JNodePosn):
        writer.write_int(jnode_position.tile_x)
        writer.write_int(jnode_position.tile_z)
        writer.write_float(jnode_position.x)
        writer.write_float(jnode_position.y)
        writer.write_float(jnode_position.z)


def write_tr_item_id(writer: BlockWriter, tr_item_id: TrItemId) -> None:
    """
    Write a track item ID to a BlockWriter.

    Writes the `TrItemId` sub-block.

    Args:
        writer (BlockWriter): Writer to write the track item ID block to.
        tr_item_id (TrItemId): The track item ID object to write.
    """
    with writer.sub_block(TokenID.TrItemId):
        writer.write_int(tr_item_id.db)
        writer.write_int(tr_item_id.db_id)