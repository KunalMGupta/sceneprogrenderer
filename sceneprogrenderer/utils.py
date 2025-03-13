import os
import bpy
import sys
import numpy as np
from mathutils import Vector

def set_clamp_factor_to_zero():
    for material in bpy.data.materials:
        if material.use_nodes:  # Check if the material uses nodes
            for node in material.node_tree.nodes:
                # print(node.type)
                if node.type == 'MIX':
                    
                    # Set the numeric Factor (first one usually)
                    factor_input = node.inputs[0]  # Accessing the first "Factor" input
                    if factor_input.name == "Factor" and isinstance(factor_input.default_value, (int, float)):
                        factor_input.default_value = 0.0
                        print(f"Numeric Factor value set to: {factor_input.default_value}")
                    else:
                        print("Numeric Factor input not found or is not editable.")


# Set up the environment texture
def add_environment_texture(image_path):
    
    # Ensure the scene has a world
    world = bpy.context.scene.world
    if not world:
        world = bpy.data.worlds.new(name="World")
        bpy.context.scene.world = world
    
    # Enable nodes for the world
    world.use_nodes = True
    nodes = world.node_tree.nodes
    links = world.node_tree.links

    # Clear existing nodes
    for node in nodes:
        nodes.remove(node)

    # Add a Background node
    bg_node = nodes.new(type='ShaderNodeBackground')
    bg_node.location = (0, 0)
    
    # Add an Environment Texture node
    env_texture_node = nodes.new(type='ShaderNodeTexEnvironment')
    env_texture_node.location = (-300, 0)
    env_texture_node.image = bpy.data.images.load(image_path)

    # Add a World Output node
    world_output_node = nodes.new(type='ShaderNodeOutputWorld')
    world_output_node.location = (200, 0)

    # Link nodes
    links.new(env_texture_node.outputs['Color'], bg_node.inputs['Color'])
    links.new(bg_node.outputs['Background'], world_output_node.inputs['Surface'])

def clear_scene():
    bpy.ops.object.select_all(action='DESELECT')
    bpy.ops.object.select_by_type(type='MESH')
    bpy.ops.object.delete()
    bpy.ops.object.select_by_type(type='CAMERA')
    bpy.ops.object.delete()
    bpy.ops.object.select_by_type(type='LIGHT')
    bpy.ops.object.delete()

def load_scene(scene_path):
    bpy.ops.wm.open_mainfile(filepath=scene_path)

def apply_smooth_shading():
    # Apply smooth shading to all meshes
    for obj in bpy.data.objects:
        if obj.type == 'MESH':
            bpy.context.view_layer.objects.active = obj
            bpy.ops.object.shade_smooth()

def save_current_scene(filepath):
    bpy.ops.wm.save_as_mainfile(filepath=filepath)

def setup_renderer_video(output_path, resolution_x=1920, resolution_y=1080, frame_rate=30, samples=100):
    render = bpy.context.scene.render
    render.engine = 'BLENDER_EEVEE_NEXT'
    render.image_settings.file_format = 'FFMPEG'
    render.ffmpeg.format = 'MPEG4'
    render.ffmpeg.codec = 'H264'
    render.ffmpeg.constant_rate_factor = 'HIGH'
    render.ffmpeg.ffmpeg_preset = 'GOOD'
    render.ffmpeg.video_bitrate = 5000
    render.resolution_x = resolution_x 
    render.resolution_y = resolution_y 
    render.resolution_percentage = 100
    render.fps = frame_rate
    render.filepath = output_path
    bpy.context.scene.cycles.samples = samples 

def setup_renderer(output_path, resolution_x=1920, resolution_y=1080, samples=100):
    render = bpy.context.scene.render
    render.engine = 'BLENDER_EEVEE_NEXT'
    render.resolution_x = resolution_x
    render.resolution_y = resolution_y
    render.filepath = output_path  # Output path
    render.image_settings.file_format = 'PNG'  # Set output format to PNG
    render.image_settings.color_mode = 'RGBA'  # Use RGBA to support transparency
    render.film_transparent = True  # Enable transparency in the render output
    bpy.context.scene.cycles.samples = samples 

def initialize_camera():
    cam_data = bpy.data.cameras.new('Camera')
    cam_ob = bpy.data.objects.new('Camera', cam_data)
    bpy.context.scene.collection.objects.link(cam_ob)
    bpy.context.scene.camera = cam_ob  # Set the camera as active
    return cam_ob

def place_camera(cam_ob, loc, looking_at):
    cx, cy, cz = loc
    point = looking_at

    cam_ob.location = Vector((cx, cy, cz))
    direction = Vector(point) - cam_ob.location
    rot_quat = direction.to_track_quat('-Z', 'Y')
    cam_ob.rotation_euler = rot_quat.to_euler()

def render_image():
    bpy.ops.render.render(write_still=True)

def animate_camera(cam_ob, cam_radius, scene_center, num_frames=360):
    scene = bpy.context.scene
    scene.frame_start = 1
    scene.frame_end = num_frames

    for frame, theta in enumerate(range(0, num_frames), start=1):
        theta_rad = np.deg2rad(theta)
        cam_ob.location = Vector((
            scene_center[0] + cam_radius * np.cos(theta_rad),
            scene_center[1] + cam_radius * np.sin(theta_rad),
            scene_center[2] + cam_radius * 0.5
        ))
        
        cam_ob.keyframe_insert(data_path="location", frame=frame)

    # Make the camera always face the target
    for frame in range(1, num_frames + 1):
        bpy.context.scene.frame_set(frame)
        direction = Vector(scene_center) - cam_ob.location
        rot_quat = direction.to_track_quat('-Z', 'Y')
        cam_ob.rotation_euler = rot_quat.to_euler()
        cam_ob.keyframe_insert(data_path="rotation_euler", frame=frame)
    
    
def render_video():
    bpy.ops.render.render(animation=True)

def add_ceiling_light(name="CeilingLight", location=None, type='POINT', energy=1000.0):
    # Add an area light at the center of the ceiling.
    # Get the highest Z coordinate (ceiling height) from all mesh objects
    max_z = float('-inf')
    min_x = float('inf')
    max_x = float('-inf')
    min_y = float('inf')
    max_y = float('-inf')

    for obj in bpy.data.objects:
        if obj.type == 'MESH':
            for vertex in obj.bound_box:
                world_vertex = obj.matrix_world @ Vector(vertex)
                max_z = max(max_z, world_vertex.z)
                min_x = min(min_x, world_vertex.x)
                max_x = max(max_x, world_vertex.x)
                min_y = min(min_y, world_vertex.y)
                max_y = max(max_y, world_vertex.y)

    # Calculate center coordinates
    center_x = (min_x + max_x) / 2
    center_y = (min_y + max_y) / 2
    
    # Create an area light for more natural illumination
    light_data = bpy.data.lights.new(name=name, type=type)
    if type == 'AREA':
        light_data.size = 2.0  # Set the size of the area light
    light_object = bpy.data.objects.new(name=name, object_data=light_data)
    
    # Set area light properties for better illumination
    light_data.energy = energy  # Adjust light intensity
    light_data.color = (1, 0.95, 0.8)  # Slightly warm white color

    # Position the light
    light_object.location = location if location else (center_x, center_y, max_z - 0.1)
    bpy.context.scene.collection.objects.link(light_object)
    
    
    print(f"Added ceiling light at coordinates: ({light_object.location.x}, {light_object.location.y}, {light_object.location.z})")
    return light_object

def adjust_ceiling_light(name="CeilingLight", location=None):
    # Adjust the position of the ceiling light.
    light = bpy.data.objects.get(name)
    if not light:
        print(f"Light '{name}' not found.")
        return None
    
    if location:
        light.location = location
        print(f"Adjusted light position to: {location}")
    return light

def get_scene_params():
    from mathutils import Vector

    # Initialize bounding box extremes
    min_x, min_y, min_z = float('inf'), float('inf'), float('inf')
    max_x, max_y, max_z = float('-inf'), float('-inf'), float('-inf')

    # Iterate over all mesh objects in the scene
    for obj in bpy.data.objects:
        if obj.type == 'MESH':
            # Transform each vertex of the object's bounding box to world coordinates
            for vertex in obj.bound_box:
                world_vertex = obj.matrix_world @ Vector(vertex)
                min_x = min(min_x, world_vertex.x)
                min_y = min(min_y, world_vertex.y)
                min_z = min(min_z, world_vertex.z)
                max_x = max(max_x, world_vertex.x)
                max_y = max(max_y, world_vertex.y)
                max_z = max(max_z, world_vertex.z)

    # Calculate scene size
    size_x = max_x - min_x
    size_y = max_y - min_y
    size_z = max_z - min_z

    # Calculate scene center
    center_x = (min_x + max_x) / 2
    center_y = (min_y + max_y) / 2
    center_z = (min_z + max_z) / 2

    # Print and return results
    print(f"scene_center=({center_x}, {center_y}, {center_z})")
    print(f"scene_size=({size_x}, {size_y}, {size_z})")

    return (center_x, center_y, center_z), (size_x, size_y, size_z)


class SceneRendererWorker:
    def __init__(self, resolution_x: int = 1920, resolution_y: int = 1080, samples: int = 100, frame_rate: int = 30, num_frames: int = 360, cuda: bool = False):
        self.resolution_x = resolution_x
        self.resolution_y = resolution_y
        self.samples = samples
        self.frame_rate = frame_rate
        self.num_frames = num_frames
        self.cuda = cuda
        self.scene_center = None
        self.scene_size = None

    def add_environment_texture(self):
        def get_image_path() -> str:
            
            # Calculate the absolute path dynamically
            package_dir = os.path.dirname(__file__)  # Directory of the current file
            image_path = os.path.join(package_dir, "assets", "env.exr")
            if not os.path.exists(image_path):
                raise FileNotFoundError(f"Image not found at {image_path}")
            return image_path

        image_path = get_image_path()

        # Add the environment texture
        add_environment_texture(image_path)

    def init(self, path):
        clear_scene()
        load_scene(path)
        apply_smooth_shading()
        set_clamp_factor_to_zero()
        cam_ob = initialize_camera()
        self.add_environment_texture()
        self.scene_center, self.scene_size = get_scene_params()
        return cam_ob

    def render(self, path, output_path, location=None, target=None):
        cam_ob = self.init(path)

        base_location = self.scene_center
        base_target = self.scene_size

         # Adjust location and target if custom inputs are provided
        if location is not None:
            base_location = [base_location[i] + location[i] for i in range(3)]
        if target is not None:
            base_target = [base_target[i] + target[i] for i in range(3)]

        base_location[1] = -base_location[1]
        base_target[1] = -base_target[1]

        place_camera(cam_ob, location, target)
        setup_renderer(output_path, self.resolution_x, self.resolution_y, self.samples)
        render_image()

    def render_from_front(self, path, output_path):
        cam_ob = self.init(path)
        scene_dims = self.scene_size
        scene_center = self.scene_center
        W, D, H = scene_dims
        cx, cz, cy = scene_center
        dist = np.max([W, D, H])
        cy_ = dist * 3.0
        # cz_ = cy_ * 0.5
        cz_ = D / 2

        place_camera(cam_ob, (cx, -cy_, cz_), (cx, cz, cy))
        setup_renderer(output_path, self.resolution_x, self.resolution_y, self.samples)
        
        render_image()

    def render_from_top(self, path, output_path):
        cam_ob = self.init(path)
        W, D, H = self.scene_size
        cx, cz, cy = self.scene_center
        dist = np.max([W, D, H])
        cy_ = dist * 3
        cz_ = cy_ * 0.5

        place_camera(cam_ob, (cx, cz, cy_), (cx, cz, 0))
        setup_renderer(output_path, self.resolution_x, self.resolution_y, self.samples)
        render_image()

    def render_from_corners(self, path, output_paths):
       
        cam_ob = self.init(path)
        scene_dims = self.scene_size
        scene_center = self.scene_center
        W,D,H = scene_dims
        cx, cz, cy = scene_center
        # cz = -cz

        corners = [
        ((cx+2*W, cz-2*D, 3*H),  (cx, cz, 0)),  # Camera at (0, 0, h) looking at (w, d, 0)
        ((cx+2*W, cz+2*D, 3*H), (cx, cz, 0)),  # Camera at (w, 0, h) looking at (0, d, 0)
        ((cx-2*W, cz+2*D, 3*H), (cx, cz, 0)),  # Camera at (0, d, h) looking at (w, 0, 0)
        ((cx-2*W, cz-2*D, 3*H),  (cx, cz, 0))   # Camera at (w, d, h) looking at (0, 0, 0)
        ]
        
        for i, (camera_location, target_location) in enumerate(corners):
            place_camera(cam_ob, camera_location, target_location)
            setup_renderer(output_paths[i], self.resolution_x, self.resolution_y, self.samples)
            render_image()
    
    def render_from_edge_midpoints(self, path, output_paths):
       
        cam_ob = self.init(path)
        scene_dims = self.scene_size
        scene_center = self.scene_center
        W, D, H = scene_dims
        cx, cz, cy = scene_center

        # Midpoints of the four upper edges
        edges = [
            ((cx + 3*W, cz, 3 * H), (cx, cz, 0)),  # Front-midpoint
            ((cx, cz + 3*D, 3 * H), (cx, cz, 0)),  # Back-midpoint
            ((cx - 3*W, cz, 3 * H), (cx, cz, 0)),  # Left-midpoint
            ((cx, cz - 3*D, 3 * H), (cx, cz, 0))   # Right-midpoint
        ]

        for i, (camera_location, target_location) in enumerate(edges):
            place_camera(cam_ob, camera_location, target_location)
            setup_renderer(output_paths[i], self.resolution_x, self.resolution_y, self.samples)
            render_image()

    def render_360(self, path, output_path):
       
        cam_ob = self.init(path)
        scene_dims = self.scene_size
        scene_center = self.scene_center
        cx, cz, cy = scene_center

        W,D,H = scene_dims
        cam_radius = 3 * np.sqrt((W / 2) ** 2 + (D / 2) ** 2)
        animate_camera(cam_ob, cam_radius, scene_center)
        setup_renderer_video(output_path, self.resolution_x, self.resolution_y, self.frame_rate, self.samples)
        render_video()