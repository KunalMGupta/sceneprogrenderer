# SceneProgRenderer

**SceneProgRenderer** is a Python-based **Blender automation tool** for rendering scenes programmatically. It allows users to generate high-quality renders, including 360-degree animations, custom camera angles, and transparent background images using Blender’s Python API.

## 🚀 Features
- **Scene Loading & Setup**
  - Clears the scene and loads a new `.blend` file.
  - Applies smooth shading and fixes materials.
  - Adds an environment texture for realistic lighting.

- **Rendering Options**
  - **Single Render**: Capture an image from a specified camera position.
  - **Front/Top Views**: Render images from standard viewpoints.
  - **Corner Views**: Automatically position the camera at four scene corners.
  - **Edge Midpoints**: Position the camera at four upper midpoints of the scene.
  - **360-Degree Animation**: Generate a rotating video render.

- **Supports Transparent Backgrounds**
  - Renders images with **RGBA** and **film transparency** for compositing.

## 📦 Installation
```bash
pip install sceneprogrenderer
```

## 📜 Usage

Importing the package:
```python
from sceneprogrenderer import SceneProgRenderer
```
### Initializing the Renderer
```python
renderer = SceneProgRenderer(
    resolution_x=1920,
    resolution_y=1080,
    samples=128,
    frame_rate=30,
    num_frames=360,
    cuda=False,
    verbose=False,
)
```
### Generic Render
```python
renderer.render(
  path="scene.blend",
  output_path="output.png",
  location=(2, 2, 2),       ## Camera location
  target=(0, 0, 0),         ## Target location
)
```

### Render from corners or edge midpoints
```python
renderer.render_from_corners(
  path="scene.blend",
  output_paths=["corner1.png", "corner2.png", "corner3.png", "corner4.png"],
)

renderer.render_from_edge_midpoints(
  path="scene.blend",
  output_paths=["edge1.png", "edge2.png", "edge3.png", "edge4.png"],
)
```

### Render from front or top views
```python
renderer.render_from_front_view(
  path="scene.blend",
  output_path="front_view.png",
)

renderer.render_from_top_view(
  path="scene.blend",
  output_path="top_view.png",
)
```

### Render 360-degree animation
```python
renderer.render_360_animation(
  path="scene.blend",
  output_path="360_animation.mp4",
)
```
