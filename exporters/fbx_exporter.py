"""
FBX ASCII exporter for Unreal Engine

v2.6.1 - Pure Python FBX ASCII writer, no external SDK required.

Export Strategy:
- Cameras: Full camera nodes with transform animation
- Meshes: Static geometry with transform animation (skip vertex-animated)
- Locators: Null nodes with animation
- Coordinate system: Y-up to Z-up conversion for Unreal Engine

FBX ASCII format based on FBX 7.4 specification.
"""

import re
from pathlib import Path
from datetime import datetime
from exporters.base_exporter import BaseExporter
from core.scene_data import SceneData, AnimationType


class FBXExporter(BaseExporter):
    """FBX ASCII file exporter for Unreal Engine"""

    def __init__(self, progress_callback=None):
        super().__init__(progress_callback)
        self.shot_name = ""
        self.fps = 24.0
        self.frame_count = 1

        # Object ID tracking (FBX uses unique 64-bit IDs)
        self._next_id = 1000000000
        self._object_ids = {}  # name -> id mapping
        self._connections = []  # List of (child_id, parent_id, property) tuples

    def _get_id(self, name):
        """Get or create unique ID for an object"""
        if name not in self._object_ids:
            self._object_ids[name] = self._next_id
            self._next_id += 1
        return self._object_ids[name]

    def get_format_name(self):
        return "FBX"

    def get_file_extension(self):
        return "fbx"

    def export(self, scene_data: SceneData, output_path, shot_name):
        """Main export method using SceneData

        Args:
            scene_data: SceneData instance with all pre-extracted animation
            output_path: Output directory
            shot_name: Shot/scene name
        """
        try:
            self.shot_name = shot_name
            self.fps = scene_data.metadata.fps
            self.frame_count = scene_data.metadata.frame_count
            self._object_ids = {}
            self._connections = []
            self._next_id = 1000000000

            self.log(f"Exporting FBX format for Unreal Engine...")

            output_dir = Path(output_path)
            self.validate_output_path(output_dir)
            fbx_file = output_dir / f"{shot_name}.fbx"

            lines = []

            # === FBX HEADER ===
            lines.extend(self._write_header())

            # === GLOBAL SETTINGS (Z-up for UE) ===
            lines.extend(self._write_global_settings())

            # === DOCUMENTS ===
            lines.extend(self._write_documents())

            # === REFERENCES ===
            lines.extend(self._write_references())

            # === DEFINITIONS ===
            # Count objects for definitions
            num_cameras = len(scene_data.cameras)
            num_meshes = sum(1 for m in scene_data.meshes
                           if m.animation_type != AnimationType.VERTEX_ANIMATED)
            num_locators = len(scene_data.transforms)
            lines.extend(self._write_definitions(num_cameras, num_meshes, num_locators))

            # === OBJECTS ===
            lines.append("Objects:  {")

            # Export cameras
            for cam in scene_data.cameras:
                display_name = cam.parent_name if cam.parent_name else cam.name
                cam_name = self._sanitize_name(display_name)
                self.log(f"  Processing camera: {cam_name}")
                lines.extend(self._write_camera(cam, cam_name))

            # Export meshes (skip vertex-animated)
            skipped_meshes = []
            for mesh in scene_data.meshes:
                display_name = mesh.parent_name if mesh.parent_name else mesh.name
                mesh_name = self._sanitize_name(display_name)

                if mesh.animation_type == AnimationType.VERTEX_ANIMATED:
                    skipped_meshes.append(mesh_name)
                    self.log(f"  Skipping vertex-animated mesh: {mesh_name}")
                    continue

                self.log(f"  Processing mesh: {mesh_name}")
                lines.extend(self._write_mesh(mesh, mesh_name))

            # Export locators/transforms
            for transform in scene_data.transforms:
                xform_name = self._sanitize_name(transform.name)
                if not transform.keyframes:
                    continue
                self.log(f"  Processing locator: {xform_name}")
                lines.extend(self._write_locator(transform, xform_name))

            # Write animation stacks
            lines.extend(self._write_animation_stack())

            lines.append("}")
            lines.append("")

            # === CONNECTIONS ===
            lines.extend(self._write_connections())

            # === TAKES ===
            lines.extend(self._write_takes())

            # Write file
            with open(fbx_file, 'w', encoding='utf-8') as f:
                f.write('\n'.join(lines))

            self.log(f"FBX file created: {fbx_file.name}")

            result = {
                'success': True,
                'fbx_file': str(fbx_file),
                'files': [str(fbx_file)],
                'message': f"FBX export complete: {fbx_file.name}"
            }

            if skipped_meshes:
                result['skipped_meshes'] = skipped_meshes
                result['message'] += f" (skipped {len(skipped_meshes)} vertex-animated meshes)"

            return result

        except Exception as e:
            error_msg = f"FBX export failed: {str(e)}"
            self.log(f"ERROR: {error_msg}")
            import traceback
            self.log(traceback.format_exc())
            return {
                'success': False,
                'message': error_msg,
                'files': []
            }

    # === COORDINATE CONVERSION ===

    def _convert_position_to_zup(self, pos):
        """Convert Y-up position to Z-up for Unreal Engine"""
        x, y, z = pos
        # Y-up to Z-up: swap Y and Z
        return (x, -z, y)

    def _convert_rotation_to_zup(self, rot):
        """Convert Y-up rotation to Z-up for Unreal Engine"""
        rx, ry, rz = rot
        # Adjust rotation for coordinate system change
        return (rx, -rz, ry)

    # === FBX STRUCTURE WRITERS ===

    def _write_header(self):
        """Write FBX ASCII header"""
        timestamp = datetime.now().strftime("%Y/%m/%d %H:%M:%S.000")
        return [
            "; FBX 7.4.0 project file",
            "; Created by MultiConverter",
            "; ----------------------------------------------------",
            "",
            "FBXHeaderExtension:  {",
            "    FBXHeaderVersion: 1003",
            "    FBXVersion: 7400",
            "    CreationTimeStamp:  {",
            f'        Version: 1000',
            f'        Year: {datetime.now().year}',
            f'        Month: {datetime.now().month}',
            f'        Day: {datetime.now().day}',
            f'        Hour: {datetime.now().hour}',
            f'        Minute: {datetime.now().minute}',
            f'        Second: {datetime.now().second}',
            f'        Millisecond: 0',
            "    }",
            '    Creator: "MultiConverter v2.6.1"',
            "    SceneInfo: \"SceneInfo::GlobalInfo\", \"UserData\" {",
            '        Type: "UserData"',
            "        Version: 100",
            "        MetaData:  {",
            "            Version: 100",
            '            Title: ""',
            '            Subject: ""',
            '            Author: ""',
            '            Keywords: ""',
            '            Revision: ""',
            '            Comment: ""',
            "        }",
            "    }",
            "}",
            "",
        ]

    def _write_global_settings(self):
        """Write global settings with Z-up axis for Unreal Engine"""
        return [
            "GlobalSettings:  {",
            "    Version: 1000",
            "    Properties70:  {",
            '        P: "UpAxis", "int", "Integer", "",2',
            '        P: "UpAxisSign", "int", "Integer", "",1',
            '        P: "FrontAxis", "int", "Integer", "",1',
            '        P: "FrontAxisSign", "int", "Integer", "",1',
            '        P: "CoordAxis", "int", "Integer", "",0',
            '        P: "CoordAxisSign", "int", "Integer", "",1',
            '        P: "OriginalUpAxis", "int", "Integer", "",1',
            '        P: "OriginalUpAxisSign", "int", "Integer", "",1',
            f'        P: "UnitScaleFactor", "double", "Number", "",1',
            f'        P: "OriginalUnitScaleFactor", "double", "Number", "",1',
            f'        P: "TimeSpanStart", "KTime", "Time", "",0',
            f'        P: "TimeSpanStop", "KTime", "Time", "",{int(self.frame_count * 46186158000 / self.fps)}',
            f'        P: "CustomFrameRate", "double", "Number", "",{self.fps}',
            "    }",
            "}",
            "",
        ]

    def _write_documents(self):
        """Write documents section"""
        return [
            "Documents:  {",
            "    Count: 1",
            "    Document: 1000000000, \"\", \"Scene\" {",
            "        Properties70:  {",
            '            P: "SourceObject", "object", "", ""',
            f'            P: "ActiveAnimStackName", "KString", "", "", "Take 001"',
            "        }",
            "        RootNode: 0",
            "    }",
            "}",
            "",
        ]

    def _write_references(self):
        """Write references section (empty for our exports)"""
        return [
            "References:  {",
            "}",
            "",
        ]

    def _write_definitions(self, num_cameras, num_meshes, num_locators):
        """Write object type definitions"""
        # Count total objects: Models + Geometry + NodeAttributes + AnimStack + AnimLayer + AnimCurveNodes + AnimCurves
        total_models = num_cameras + num_meshes + num_locators
        total_geometry = num_meshes
        total_node_attrs = num_cameras + num_locators  # Camera and Null attributes

        return [
            "Definitions:  {",
            "    Version: 100",
            f"    Count: {4 + total_models + total_geometry + total_node_attrs}",
            "    ObjectType: \"GlobalSettings\" {",
            "        Count: 1",
            "    }",
            f'    ObjectType: "Model" {{',
            f"        Count: {total_models}",
            "        PropertyTemplate: \"FbxNode\" {",
            "            Properties70:  {",
            '                P: "Lcl Translation", "Lcl Translation", "", "A",0,0,0',
            '                P: "Lcl Rotation", "Lcl Rotation", "", "A",0,0,0',
            '                P: "Lcl Scaling", "Lcl Scaling", "", "A",1,1,1',
            "            }",
            "        }",
            "    }",
            f'    ObjectType: "Geometry" {{',
            f"        Count: {total_geometry}",
            "    }",
            f'    ObjectType: "NodeAttribute" {{',
            f"        Count: {total_node_attrs}",
            "    }",
            '    ObjectType: "AnimationStack" {',
            "        Count: 1",
            "    }",
            '    ObjectType: "AnimationLayer" {',
            "        Count: 1",
            "    }",
            "}",
            "",
        ]

    def _write_camera(self, cam_data, cam_name):
        """Write camera node and attributes"""
        lines = []

        model_id = self._get_id(f"Model::{cam_name}")
        attr_id = self._get_id(f"NodeAttribute::{cam_name}")

        # Get initial transform (converted to Z-up)
        if cam_data.keyframes:
            kf = cam_data.keyframes[0]
            pos = self._convert_position_to_zup(kf.position)
            rot = self._convert_rotation_to_zup(kf.rotation_maya)
        else:
            pos = (0, 0, 0)
            rot = (0, 0, 0)

        focal_length = cam_data.properties.focal_length

        # Camera attribute
        lines.extend([
            f'    NodeAttribute: {attr_id}, "NodeAttribute::{cam_name}", "Camera" {{',
            '        Properties70:  {',
            f'            P: "FocalLength", "Number", "", "A",{focal_length}',
            '            P: "CameraProjectionType", "enum", "", "",0',
            '        }',
            '        TypeFlags: "Camera"',
            '    }',
        ])

        # Camera model
        lines.extend([
            f'    Model: {model_id}, "Model::{cam_name}", "Camera" {{',
            '        Version: 232',
            '        Properties70:  {',
            f'            P: "Lcl Translation", "Lcl Translation", "", "A",{pos[0]:.6f},{pos[1]:.6f},{pos[2]:.6f}',
            f'            P: "Lcl Rotation", "Lcl Rotation", "", "A",{rot[0]:.6f},{rot[1]:.6f},{rot[2]:.6f}',
            '            P: "Lcl Scaling", "Lcl Scaling", "", "A",1,1,1',
            '        }',
            '        Shading: Y',
            '        Culling: "CullingOff"',
            '    }',
        ])

        # Connect attribute to model
        self._connections.append((attr_id, model_id, None))
        # Connect model to root (0)
        self._connections.append((model_id, 0, None))

        # Add animation curves
        self._add_animation_curves(cam_data.keyframes, cam_name, lines)

        return lines

    def _write_mesh(self, mesh_data, mesh_name):
        """Write mesh geometry and model node"""
        lines = []

        model_id = self._get_id(f"Model::{mesh_name}")
        geom_id = self._get_id(f"Geometry::{mesh_name}")

        # Get initial transform (converted to Z-up)
        if mesh_data.keyframes:
            kf = mesh_data.keyframes[0]
            pos = self._convert_position_to_zup(kf.position)
            rot = self._convert_rotation_to_zup(kf.rotation_maya)
            scale = kf.scale
        else:
            pos = (0, 0, 0)
            rot = (0, 0, 0)
            scale = (1, 1, 1)

        # === GEOMETRY ===
        positions = mesh_data.geometry.positions
        indices = mesh_data.geometry.indices
        counts = mesh_data.geometry.counts

        # Convert positions to Z-up
        converted_positions = [self._convert_position_to_zup(p) for p in positions]

        # Flatten positions for FBX format
        pos_array = []
        for p in converted_positions:
            pos_array.extend([p[0], p[1], p[2]])

        # Build polygon vertex indices (negative marks end of polygon in FBX)
        poly_indices = []
        idx_offset = 0
        for count in counts:
            for i in range(count - 1):
                poly_indices.append(indices[idx_offset + i])
            # Last index is negative (XOR with -1)
            poly_indices.append(-indices[idx_offset + count - 1] - 1)
            idx_offset += count

        lines.extend([
            f'    Geometry: {geom_id}, "Geometry::{mesh_name}", "Mesh" {{',
            f'        Vertices: *{len(pos_array)} {{',
            f'            a: {",".join(f"{v:.6f}" for v in pos_array)}',
            '        }',
            f'        PolygonVertexIndex: *{len(poly_indices)} {{',
            f'            a: {",".join(str(i) for i in poly_indices)}',
            '        }',
            '        GeometryVersion: 124',
            '        LayerElementNormal: 0 {',
            '            Version: 102',
            '            Name: ""',
            '            MappingInformationType: "ByPolygonVertex"',
            '            ReferenceInformationType: "Direct"',
            '            Normals: *0 {',
            '                a: ',
            '            }',
            '        }',
            '        Layer: 0 {',
            '            Version: 100',
            '            LayerElement:  {',
            '                Type: "LayerElementNormal"',
            '                TypedIndex: 0',
            '            }',
            '        }',
            '    }',
        ])

        # === MODEL ===
        lines.extend([
            f'    Model: {model_id}, "Model::{mesh_name}", "Mesh" {{',
            '        Version: 232',
            '        Properties70:  {',
            f'            P: "Lcl Translation", "Lcl Translation", "", "A",{pos[0]:.6f},{pos[1]:.6f},{pos[2]:.6f}',
            f'            P: "Lcl Rotation", "Lcl Rotation", "", "A",{rot[0]:.6f},{rot[1]:.6f},{rot[2]:.6f}',
            f'            P: "Lcl Scaling", "Lcl Scaling", "", "A",{scale[0]:.6f},{scale[1]:.6f},{scale[2]:.6f}',
            '        }',
            '        Shading: Y',
            '        Culling: "CullingOff"',
            '    }',
        ])

        # Connect geometry to model
        self._connections.append((geom_id, model_id, None))
        # Connect model to root (0)
        self._connections.append((model_id, 0, None))

        # Add animation curves if animated
        if mesh_data.animation_type == AnimationType.TRANSFORM_ONLY:
            self._add_animation_curves(mesh_data.keyframes, mesh_name, lines)

        return lines

    def _write_locator(self, transform_data, loc_name):
        """Write locator/null node"""
        lines = []

        model_id = self._get_id(f"Model::{loc_name}")
        attr_id = self._get_id(f"NodeAttribute::{loc_name}")

        # Get initial transform (converted to Z-up)
        if transform_data.keyframes:
            kf = transform_data.keyframes[0]
            pos = self._convert_position_to_zup(kf.position)
            rot = self._convert_rotation_to_zup(kf.rotation_maya)
            scale = kf.scale
        else:
            pos = (0, 0, 0)
            rot = (0, 0, 0)
            scale = (1, 1, 1)

        # Null attribute
        lines.extend([
            f'    NodeAttribute: {attr_id}, "NodeAttribute::{loc_name}", "Null" {{',
            '        TypeFlags: "Null"',
            '    }',
        ])

        # Null model
        lines.extend([
            f'    Model: {model_id}, "Model::{loc_name}", "Null" {{',
            '        Version: 232',
            '        Properties70:  {',
            f'            P: "Lcl Translation", "Lcl Translation", "", "A",{pos[0]:.6f},{pos[1]:.6f},{pos[2]:.6f}',
            f'            P: "Lcl Rotation", "Lcl Rotation", "", "A",{rot[0]:.6f},{rot[1]:.6f},{rot[2]:.6f}',
            f'            P: "Lcl Scaling", "Lcl Scaling", "", "A",{scale[0]:.6f},{scale[1]:.6f},{scale[2]:.6f}',
            '        }',
            '        Shading: Y',
            '        Culling: "CullingOff"',
            '    }',
        ])

        # Connect attribute to model
        self._connections.append((attr_id, model_id, None))
        # Connect model to root (0)
        self._connections.append((model_id, 0, None))

        # Add animation curves
        self._add_animation_curves(transform_data.keyframes, loc_name, lines)

        return lines

    def _add_animation_curves(self, keyframes, obj_name, lines):
        """Add animation curve nodes for an object"""
        if not keyframes or len(keyframes) < 2:
            return

        model_id = self._get_id(f"Model::{obj_name}")
        anim_layer_id = self._get_id("AnimationLayer::BaseLayer")

        # Time conversion: frames to FBX time (46186158000 units per second)
        time_scale = 46186158000 / self.fps

        def is_animated(vals):
            return len(set(round(v, 4) for v in vals)) > 1

        # Extract and convert values
        times = [int(kf.frame * time_scale) for kf in keyframes]

        # Convert positions to Z-up
        positions = [self._convert_position_to_zup(kf.position) for kf in keyframes]
        tx = [p[0] for p in positions]
        ty = [p[1] for p in positions]
        tz = [p[2] for p in positions]

        # Convert rotations to Z-up
        rotations = [self._convert_rotation_to_zup(kf.rotation_maya) for kf in keyframes]
        rx = [r[0] for r in rotations]
        ry = [r[1] for r in rotations]
        rz = [r[2] for r in rotations]

        channels = [
            ('T', 'Lcl Translation', [
                ('X', tx), ('Y', ty), ('Z', tz)
            ]),
            ('R', 'Lcl Rotation', [
                ('X', rx), ('Y', ry), ('Z', rz)
            ]),
        ]

        for prefix, prop_name, axes in channels:
            # Check if any axis is animated
            if not any(is_animated(vals) for _, vals in axes):
                continue

            # AnimCurveNode
            curve_node_id = self._get_id(f"AnimCurveNode::{obj_name}_{prefix}")

            default_vals = [axes[0][1][0], axes[1][1][0], axes[2][1][0]]

            lines.extend([
                f'    AnimationCurveNode: {curve_node_id}, "AnimCurveNode::{prefix}", "" {{',
                '        Properties70:  {',
                f'            P: "d|X", "Number", "", "A",{default_vals[0]:.6f}',
                f'            P: "d|Y", "Number", "", "A",{default_vals[1]:.6f}',
                f'            P: "d|Z", "Number", "", "A",{default_vals[2]:.6f}',
                '        }',
                '    }',
            ])

            # Connect curve node to layer and model
            self._connections.append((curve_node_id, anim_layer_id, None))
            self._connections.append((curve_node_id, model_id, prop_name))

            # AnimCurves for each axis
            for axis_name, vals in axes:
                if not is_animated(vals):
                    continue

                curve_id = self._get_id(f"AnimCurve::{obj_name}_{prefix}_{axis_name}")

                # Build keyframe data
                key_count = len(times)
                time_str = ",".join(str(t) for t in times)
                val_str = ",".join(f"{v:.6f}" for v in vals)

                # AttrFlags: all linear interpolation
                attr_flags = ",".join(["24836"] * key_count)
                # AttrData: 4 zeros per key (tangent data)
                attr_data = ",".join(["0,0,0,0"] * key_count)

                lines.extend([
                    f'    AnimationCurve: {curve_id}, "AnimCurve::", "" {{',
                    '        Default: 0',
                    f'        KeyVer: 4009',
                    f'        KeyTime: *{key_count} {{',
                    f'            a: {time_str}',
                    '        }',
                    f'        KeyValueFloat: *{key_count} {{',
                    f'            a: {val_str}',
                    '        }',
                    f'        KeyAttrFlags: *{key_count} {{',
                    f'            a: {attr_flags}',
                    '        }',
                    f'        KeyAttrDataFloat: *{key_count * 4} {{',
                    f'            a: {attr_data}',
                    '        }',
                    f'        KeyAttrRefCount: *{key_count} {{',
                    f'            a: {",".join(["1"] * key_count)}',
                    '        }',
                    '    }',
                ])

                # Connect curve to curve node
                self._connections.append((curve_id, curve_node_id, f"d|{axis_name}"))

    def _write_animation_stack(self):
        """Write animation stack and layer"""
        lines = []

        stack_id = self._get_id("AnimationStack::Take001")
        layer_id = self._get_id("AnimationLayer::BaseLayer")

        # Time span
        time_scale = 46186158000 / self.fps
        end_time = int(self.frame_count * time_scale)

        lines.extend([
            f'    AnimationStack: {stack_id}, "AnimStack::Take 001", "" {{',
            '        Properties70:  {',
            f'            P: "LocalStop", "KTime", "Time", "",{end_time}',
            f'            P: "ReferenceStop", "KTime", "Time", "",{end_time}',
            '        }',
            '    }',
            f'    AnimationLayer: {layer_id}, "AnimLayer::BaseLayer", "" {{',
            '    }',
        ])

        # Connect layer to stack
        self._connections.append((layer_id, stack_id, None))

        return lines

    def _write_connections(self):
        """Write all object connections"""
        lines = [
            "Connections:  {",
        ]

        for child_id, parent_id, prop in self._connections:
            if prop:
                # Property connection
                lines.append(f'    C: "OP",{child_id},{parent_id}, "{prop}"')
            else:
                # Object-Object connection
                lines.append(f'    C: "OO",{child_id},{parent_id}')

        lines.append("}")
        lines.append("")

        return lines

    def _write_takes(self):
        """Write takes section"""
        time_scale = 46186158000 / self.fps
        end_time = int(self.frame_count * time_scale)

        return [
            "Takes:  {",
            '    Current: "Take 001"',
            '    Take: "Take 001" {',
            f'        FileName: "Take_001.tak"',
            f'        LocalTime: 0,{end_time}',
            f'        ReferenceTime: 0,{end_time}',
            '    }',
            "}",
            "",
        ]

    # === UTILITIES ===

    def _sanitize_name(self, name):
        """Sanitize name for FBX"""
        sanitized = re.sub(r'[^a-zA-Z0-9_]', '_', name)
        if sanitized and sanitized[0].isdigit():
            sanitized = f"obj_{sanitized}"
        return sanitized or "unnamed"
