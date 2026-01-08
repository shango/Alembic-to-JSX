import Alembic  # pyalembic
import numpy as np
import json

# ----------------------------
# User settings
# ----------------------------
abc_file = "scene.abc"      # Input Alembic
jsx_file = "scene.jsx"      # Output JSX
fps = 30                     # AE composition fps
duration = 5                 # Duration in seconds
comp_width, comp_height = 1920, 1080
comp_depth = 1

# ----------------------------
# Open Alembic
# ----------------------------
archive = Alembic.IArchive(abc_file)
top_obj = archive.getTop()

objects = []

def traverse(obj):
    objects.append(obj)
    for child in obj.children:
        traverse(child)

traverse(top_obj)

# ----------------------------
# Transform helpers
# ----------------------------
def extract_translation(obj):
    m = np.array(obj.getMatrix())
    x, y, z = m[0,3], m[1,3], m[2,3]
    return [x, y, z]  # Y-up retained

def extract_scale(obj):
    m = np.array(obj.getMatrix())
    sx = np.linalg.norm(m[0,:3])
    sy = np.linalg.norm(m[1,:3])
    sz = np.linalg.norm(m[2,:3])
    return [sx, sy, sz]

def extract_rotation(obj):
    m = np.array(obj.getMatrix())
    sy = np.sqrt(m[0,0]**2 + m[1,0]**2)
    if sy < 1e-6:
        x = np.arctan2(-m[1,2], m[1,1])
        y = np.arctan2(-m[2,0], sy)
        z = 0
    else:
        x = np.arctan2(m[2,1], m[2,2])
        y = np.arctan2(-m[2,0], sy)
        z = np.arctan2(m[1,0], m[0,0])
    return [np.degrees(x), np.degrees(y), np.degrees(z)]

# ----------------------------
# Generate JSX
# ----------------------------
jsx_lines = []
jsx_lines.append("// Auto-generated JSX from Alembic")
jsx_lines.append(f"var comp = app.project.items.addComp('Scene', {comp_width}, {comp_height}, {comp_depth}, {duration}, {fps});")

for obj in objects:
    name = obj.getName()
    
    # Detect cameras if supported
    if obj.isCamera():
        jsx_lines.append(f"var cam = comp.layers.addCamera('{name}', [0,0]);")
        layer_name = "cam"
    else:
        jsx_lines.append(f"var nullLayer = comp.layers.addNull();")
        jsx_lines.append(f"nullLayer.name = '{name}';")
        jsx_lines.append("nullLayer.threeDLayer = true;")
        layer_name = "nullLayer"

    for f_index in range(int(duration*fps)):
        t = f_index / fps
        pos = extract_translation(obj)
        rot = extract_rotation(obj)
        scale = extract_scale(obj)

        jsx_lines.append(f"{layer_name}.property('Position').setValueAtTime({t}, [{pos[0]}, {pos[1]}, {pos[2]}]);")
        jsx_lines.append(f"{layer_name}.property('X Rotation').setValueAtTime({t}, {rot[0]});")
        jsx_lines.append(f"{layer_name}.property('Y Rotation').setValueAtTime({t}, {rot[1]});")
        jsx_lines.append(f"{layer_name}.property('Z Rotation').setValueAtTime({t}, {rot[2]});")
        jsx_lines.append(f"{layer_name}.property('Scale').setValueAtTime({t}, [{scale[0]*100}, {scale[1]*100}, {scale[2]*100}]);")

# ----------------------------
# Write JSX file
# ----------------------------
with open(jsx_file, 'w') as f:
    f.write("\n".join(jsx_lines))

print(f"JSX written to {jsx_file}. Import in AE 2025, 3D nulls and cameras created with Y-up and original scene scale.")
