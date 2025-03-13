import bpy
from mathutils import Vector
import os
import json

import sys
sys.path.append('/Users/kunalgupta/Documents/blender_packages')
import numpy as np
import trimesh


def render_360_videos():
    with open('sceneprog_params.txt', 'r') as f:
        glb_directory = f.readline().strip()
        output_directory = f.readline().strip()
        downsample = 2  # Set resolution scaling factor

    def get_whd(scene_path):
        ## load floor.glb
        floor_path = scene_path + '/floor.glb'
        floor = trimesh.load(floor_path,force='mesh',process=False)
        bounds = floor.bounds
        d,w = bounds[1,0], bounds[1,2]
        
        ## load back_wall.glb
        back_wall_path = scene_path + '/back_wall.glb'
        back_wall = trimesh.load(back_wall_path,force='mesh',process=False)
        bounds = back_wall.bounds
        h = bounds[1,1]
        return d,h,w

    # Configure video output
    def configure_video_output(output_path, frame_rate=30):
        render = bpy.context.scene.render
        render.engine = 'BLENDER_EEVEE_NEXT'
        render.image_settings.file_format = 'FFMPEG'
        render.ffmpeg.format = 'MPEG4'
        render.ffmpeg.codec = 'H264'
        render.ffmpeg.constant_rate_factor = 'HIGH'
        render.ffmpeg.ffmpeg_preset = 'GOOD'
        render.ffmpeg.video_bitrate = 5000
        render.resolution_x = 1920 // downsample
        render.resolution_y = 1080 // downsample
        render.resolution_percentage = 100
        render.fps = frame_rate
        render.filepath = output_path

    # Animate camera around the scene
    def animate_camera(cam_ob, cam_radius, target_location, w, d, h, frame_rate):
        num_frames = 360  # One frame per degree for smooth rotation
        scene = bpy.context.scene
        scene.frame_start = 1
        scene.frame_end = num_frames

        for frame, theta in enumerate(range(0, 360), start=1):
            theta_rad = np.deg2rad(theta)
            cam_ob.location = Vector((
                w / 2 + cam_radius * np.cos(theta_rad),
                -d / 2 + cam_radius * np.sin(theta_rad),
                2 * h / 3
            ))
            cam_ob.keyframe_insert(data_path="location", frame=frame)

        # Make the camera always face the target
        for frame in range(1, num_frames + 1):
            bpy.context.scene.frame_set(frame)
            direction = target_location - cam_ob.location
            rot_quat = direction.to_track_quat('-Z', 'Y')
            cam_ob.rotation_euler = rot_quat.to_euler()
            cam_ob.keyframe_insert(data_path="rotation_euler", frame=frame)

    # Clear existing objects
    bpy.ops.wm.read_factory_settings(use_empty=True)

    # Import GLB file
    bpy.ops.import_scene.gltf(filepath=os.path.join(glb_directory, 'scene.glb'))

    ceiling_object = bpy.data.objects.get('ceiling.glb')
    if ceiling_object:
        bpy.data.objects.remove(ceiling_object, do_unlink=True)

    # Apply smooth shading
    for obj in bpy.data.objects:
        if obj.type == 'MESH':
            bpy.context.view_layer.objects.active = obj
            bpy.ops.object.shade_smooth()

    # Find and remove ceiling
    ceiling_object = bpy.data.objects.get('ceiling.glb')
    if ceiling_object:
        bpy.data.objects.remove(ceiling_object, do_unlink=True)

    w, h, d = get_whd(glb_directory)
    maxdim = max(w, d)
    cam_radius = 3 * np.sqrt((w / 2) ** 2 + (d / 2) ** 2)
    target_location = Vector((w / 2, -d / 2, h / 2))

    # Add light
    light_data = bpy.data.lights.new(name='AreaLight', type='AREA')
    light_ob = bpy.data.objects.new(name='AreaLight', object_data=light_data)
    bpy.context.collection.objects.link(light_ob)
    light_ob.location = (w / 2, -d / 2, h + 0.1)  # Slightly above the ceiling
    light_data.energy = 3000  # Increased energy for better visibility
    light_data.shape = 'RECTANGLE'
    light_data.size = maxdim
    light_data.size_y = maxdim

    # Add camera
    cam_data = bpy.data.cameras.new('Camera')
    cam_ob = bpy.data.objects.new('Camera', cam_data)
    bpy.context.scene.collection.objects.link(cam_ob)
    bpy.context.scene.camera = cam_ob

    # Animate camera
    animate_camera(cam_ob, cam_radius, target_location, w, d, h, frame_rate=30)

    # Configure video output
    video_output_path = os.path.join(output_directory, 'scene_render.mp4')
    configure_video_output(video_output_path)

    # Render animation
    bpy.ops.render.render(animation=True)
    print(f"Rendered 360-degree video to {video_output_path}.")

if __name__ == "__main__":
    render_360_videos()