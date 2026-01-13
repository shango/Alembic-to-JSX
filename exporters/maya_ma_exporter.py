"""
Maya ASCII (.ma) exporter with Alembic reference for vertex animation

Export Strategy:
- Cameras: Full geometry with animCurve nodes
- Transforms: animCurve nodes for translate/rotate/scale
- Static/Transform-only meshes: Full geometry embedded in .ma
- Vertex-animated meshes: Reference original Alembic via AlembicNode
"""

import re
from pathlib import Path
from datetime import datetime
from exporters.base_exporter import BaseExporter


class MayaMAExporter(BaseExporter):
    """Maya ASCII (.ma) file exporter"""

    def __init__(self, progress_callback=None):
        super().__init__(progress_callback)
        self.maya_version = "2020"
        self.shot_name = ""

    def get_format_name(self):
        return "Maya MA"

    def get_file_extension(self):
        return "ma"

    def export(self, reader, output_path, shot_name, fps, frame_count, animation_data, abc_file_path=None):
        """
        Main export method

        Args:
            reader: AlembicReader instance
            output_path: Output directory path
            shot_name: Shot name for file naming
            fps: Frames per second
            frame_count: Total frame count
            animation_data: Dict with 'vertex_animated', 'transform_only', 'static' lists
            abc_file_path: Path to original Alembic file (for AlembicNode references)

        Returns:
            Dict with keys: 'success', 'ma_file', 'files', 'message'
        """
        try:
            self.shot_name = shot_name
            self.log(f"Exporting Maya MA format...")

            # Validate output path
            output_dir = Path(output_path)
            self.validate_output_path(output_dir)

            # Generate .ma file
            ma_file = output_dir / f"{shot_name}.ma"

            # Build .ma content
            lines = []

            # Header
            lines.extend(self._generate_header())

            # Requirements
            has_vertex_anim = len(animation_data.get('vertex_animated', [])) > 0
            lines.extend(self._generate_requirements(has_vertex_anim))

            # Units
            lines.extend(self._generate_units(fps))

            # File info
            lines.extend(self._generate_file_info(abc_file_path))

            # Create scene nodes
            lines.extend(self._generate_scene_nodes(
                reader, fps, frame_count, animation_data, abc_file_path
            ))

            # Write to file
            with open(ma_file, 'w', encoding='utf-8') as f:
                f.write('\n'.join(lines))

            self.log(f"✓ Maya MA file created: {ma_file.name}")

            result = {
                'success': True,
                'ma_file': str(ma_file),
                'files': [str(ma_file)],
                'message': f"Maya MA export complete: {ma_file.name}"
            }

            # Add warning about Alembic dependency if vertex animation present
            if has_vertex_anim:
                result['message'] += f"\n⚠ Vertex-animated meshes reference original Alembic file"

            return result

        except Exception as e:
            error_msg = f"Maya MA export failed: {str(e)}"
            self.log(f"✗ {error_msg}")
            return {
                'success': False,
                'message': error_msg,
                'files': []
            }

    # === HEADER GENERATION ===

    def _generate_header(self):
        """Generate Maya .ma file header"""
        timestamp = datetime.now().strftime("%a, %b %d, %Y %I:%M:%S %p")
        return [
            f"//Maya ASCII {self.maya_version} scene",
            f"//Name: {self.shot_name}.ma",
            f"//Last modified: {timestamp}",
            "//Codeset: UTF-8"
        ]

    def _generate_requirements(self, has_vertex_anim=False):
        """Generate requirements section"""
        lines = [f'requires maya "{self.maya_version}";']
        if has_vertex_anim:
            lines.append('requires "AbcImport" "1.0";')
        return lines

    def _generate_units(self, fps):
        """Generate units configuration"""
        return [
            'currentUnit -l centimeter -a degree -t film;',
            f'currentUnit -t "{fps}fps";'
        ]

    def _generate_file_info(self, abc_filename=None):
        """Generate file metadata"""
        lines = [
            'fileInfo "application" "abcConverter";',
            'fileInfo "product" "Maya 2020";',
            'fileInfo "version" "2020";'
        ]
        if abc_filename:
            lines.append(f'fileInfo "sourceAlembic" "{self._mel_escape_string(abc_filename)}";')
        return lines

    # === NODE CREATION ===

    def _create_transform_node(self, name, parent=None):
        """Create transform node with optional parent"""
        lines = []
        if parent:
            lines.append(f'createNode transform -n "{name}" -p "{parent}";')
        else:
            lines.append(f'createNode transform -n "{name}";')
        return lines

    def _create_camera_node(self, name, parent_transform, focal_length, h_aperture, v_aperture):
        """Create camera shape node"""
        return [
            f'createNode camera -n "{name}" -p "{parent_transform}";',
            f'    setAttr -k off ".v";',
            f'    setAttr ".fl" {focal_length};',
            f'    setAttr ".hfa" {h_aperture * 10};',  # cm to mm
            f'    setAttr ".vfa" {v_aperture * 10};',  # cm to mm
            f'    setAttr ".fd" 5.0;',  # focus distance
            f'    setAttr ".coi" 5.0;'  # center of interest
        ]

    def _create_mesh_node(self, name, parent_transform):
        """Create mesh shape node"""
        return [
            f'createNode mesh -n "{name}" -p "{parent_transform}";',
            f'    setAttr -k off ".v";',
            f'    setAttr ".vir" yes;',
            f'    setAttr ".vif" yes;',
            f'    setAttr ".uvst[0].uvsn" -type "string" "map1";',
            f'    setAttr ".cuvs" -type "string" "map1";'
        ]

    def _create_alembic_reference_node(self, mesh_name, abc_file_path, alembic_path):
        """Create AlembicNode for vertex-animated mesh"""
        alembic_node = f"{mesh_name}_alembicNode"
        lines = [
            f'createNode AlembicNode -n "{alembic_node}";',
            f'    setAttr ".abc_File" -type "string" "{self._mel_escape_string(abc_file_path)}";',
            f'    setAttr ".abc_layerFileName" -type "string" "";',
            f'    setAttr ".time" 1;'
        ]
        return lines, alembic_node

    # === ATTRIBUTE SETTING ===

    def _set_transform_static(self, node_name, pos, rot, scale):
        """Set static transform attributes"""
        return [
            f'    setAttr ".t" -type "double3" {pos[0]} {pos[1]} {pos[2]};',
            f'    setAttr ".r" -type "double3" {rot[0]} {rot[1]} {rot[2]};',
            f'    setAttr ".s" -type "double3" {scale[0]} {scale[1]} {scale[2]};'
        ]

    def _set_mesh_vertices(self, mesh_node, positions):
        """Set mesh vertex positions"""
        vertex_count = len(positions)
        lines = [f'    setAttr ".vt[0:{vertex_count-1}]"']
        for i, pos in enumerate(positions):
            lines.append(f'        {pos[0]} {pos[1]} {pos[2]}')
        lines[-1] += ';'
        return lines

    def _set_mesh_faces(self, mesh_node, indices, counts):
        """Set mesh face topology"""
        lines = []

        # Face counts
        face_count = len(counts)
        lines.append(f'    setAttr -s {face_count} ".fc[0:{face_count-1}]"')
        for count in counts:
            lines.append(f'        {count}')
        lines[-1] += ';'

        # Face indices
        lines.append(f'    setAttr -s {len(indices)} ".pt[0:{len(indices)-1}]"')
        for idx in indices:
            lines.append(f'        {idx}')
        lines[-1] += ';'

        return lines

    # === ANIMATION ===

    def _create_anim_curve(self, node_name, attr_name, attr_type, times, values, fps):
        """
        Create animCurve node

        Args:
            node_name: Target node name
            attr_name: Attribute name (e.g., "translateX")
            attr_type: Curve type ("TL", "TA", "TU")
            times: List of frame numbers
            values: List of values
            fps: Frames per second
        """
        curve_name = f"{node_name}_{attr_name}"
        curve_type = f"animCurve{attr_type}"

        lines = [
            f'createNode {curve_type} -n "{curve_name}";',
            f'    setAttr ".tan" 18;',  # 18 = linear tangent
            f'    setAttr ".wgt" no;',
            f'    setAttr -s {len(times)} ".ktv[0:{len(times)-1}]"'
        ]

        for frame, value in zip(times, values):
            lines.append(f'        {frame} {value}')
        lines[-1] += ';'

        return lines, curve_name

    def _connect_anim_curve(self, curve_name, node_name, attr_shortname):
        """Connect animCurve to node attribute"""
        return [f'connectAttr "{curve_name}.o" "{node_name}.{attr_shortname}";']

    # === SCENE GENERATION ===

    def _generate_scene_nodes(self, reader, fps, frame_count, animation_data, abc_file_path):
        """Generate all scene nodes (cameras, meshes, animation)"""
        lines = []

        # Get scene objects
        cameras = reader.get_cameras()
        meshes = reader.get_meshes()

        # Process cameras
        for cam in cameras:
            cam_name = self._sanitize_name(cam.getName())
            self.log(f"  Processing camera: {cam_name}")

            lines.extend(self._export_camera(
                reader, cam, cam_name, fps, frame_count
            ))

        # Process meshes
        for mesh in meshes:
            mesh_name = self._sanitize_name(mesh.getName())

            # Check animation type
            if mesh_name in animation_data.get('vertex_animated', []):
                self.log(f"  Processing vertex-animated mesh: {mesh_name} (Alembic reference)")
                lines.extend(self._export_vertex_animated_mesh(
                    mesh, mesh_name, abc_file_path
                ))
            else:
                self.log(f"  Processing static/transform mesh: {mesh_name}")
                is_animated = mesh_name in animation_data.get('transform_only', [])
                lines.extend(self._export_static_mesh(
                    reader, mesh, mesh_name, fps, frame_count, is_animated
                ))

        return lines

    def _export_camera(self, reader, cam, cam_name, fps, frame_count):
        """Export camera with animation"""
        lines = []

        # Create transform
        lines.extend(self._create_transform_node(cam_name))

        # Get camera properties at frame 1
        props = reader.get_camera_properties(cam, 1.0 / fps)
        focal_length = props.get('focal_length', 35.0)
        h_aperture = props.get('h_aperture', 36.0)
        v_aperture = props.get('v_aperture', 24.0)

        # Create camera shape
        lines.extend(self._create_camera_node(
            f"{cam_name}Shape", cam_name, focal_length, h_aperture, v_aperture
        ))

        # Animate transform
        lines.extend(self._animate_transform(
            reader, cam, cam_name, fps, frame_count
        ))

        return lines

    def _export_static_mesh(self, reader, mesh, mesh_name, fps, frame_count, is_animated):
        """Export static or transform-animated mesh"""
        lines = []

        # Create transform
        lines.extend(self._create_transform_node(mesh_name))

        # Create mesh shape
        mesh_shape = f"{mesh_name}Shape"
        lines.extend(self._create_mesh_node(mesh_shape, mesh_name))

        # Get geometry at frame 1
        mesh_data = reader.get_mesh_data_at_time(mesh, 1.0 / fps)
        positions = mesh_data['positions']
        indices = mesh_data['indices']
        counts = mesh_data['counts']

        # Set geometry
        lines.extend(self._set_mesh_vertices(mesh_shape, positions))
        lines.extend(self._set_mesh_faces(mesh_shape, indices, counts))

        # Animate transform if needed
        if is_animated:
            lines.extend(self._animate_transform(
                reader, mesh, mesh_name, fps, frame_count
            ))

        return lines

    def _export_vertex_animated_mesh(self, mesh, mesh_name, abc_file_path):
        """Export vertex-animated mesh via Alembic reference"""
        lines = []

        # Create transform
        lines.extend(self._create_transform_node(mesh_name))

        # Create empty mesh shape
        mesh_shape = f"{mesh_name}Shape"
        lines.extend(self._create_mesh_node(mesh_shape, mesh_name))

        # Create AlembicNode reference
        alembic_lines, alembic_node = self._create_alembic_reference_node(
            mesh_name, abc_file_path, mesh.getFullName()
        )
        lines.extend(alembic_lines)

        # Connect Alembic to mesh
        lines.append(f'connectAttr "{alembic_node}.outPolyMesh[0]" "{mesh_shape}.inMesh";')
        lines.append(f'connectAttr "time1.outTime" "{alembic_node}.time";')

        return lines

    def _animate_transform(self, reader, obj, node_name, fps, frame_count):
        """Create animation curves for transform"""
        lines = []

        # Sample animation at each frame
        times = []
        tx_vals, ty_vals, tz_vals = [], [], []
        rx_vals, ry_vals, rz_vals = [], [], []
        sx_vals, sy_vals, sz_vals = [], [], []

        for frame in range(1, frame_count + 1):
            time_sec = frame / fps
            pos, rot, scale = reader.get_transform_at_time(obj, time_sec)

            times.append(frame)
            tx_vals.append(pos[0])
            ty_vals.append(pos[1])
            tz_vals.append(pos[2])
            rx_vals.append(rot[0])
            ry_vals.append(rot[1])
            rz_vals.append(rot[2])
            sx_vals.append(scale[0])
            sy_vals.append(scale[1])
            sz_vals.append(scale[2])

        # Check if actually animated (values change)
        def is_varying(values):
            return len(set(round(v, 6) for v in values)) > 1

        # Create curves only for animated attributes
        attrs = [
            ('translateX', 'TL', 'tx', tx_vals),
            ('translateY', 'TL', 'ty', ty_vals),
            ('translateZ', 'TL', 'tz', tz_vals),
            ('rotateX', 'TA', 'rx', rx_vals),
            ('rotateY', 'TA', 'ry', ry_vals),
            ('rotateZ', 'TA', 'rz', rz_vals),
            ('scaleX', 'TU', 'sx', sx_vals),
            ('scaleY', 'TU', 'sy', sy_vals),
            ('scaleZ', 'TU', 'sz', sz_vals)
        ]

        for attr_name, attr_type, shortname, values in attrs:
            if is_varying(values):
                curve_lines, curve_name = self._create_anim_curve(
                    node_name, attr_name, attr_type, times, values, fps
                )
                lines.extend(curve_lines)
                lines.extend(self._connect_anim_curve(curve_name, node_name, shortname))

        return lines

    # === UTILITIES ===

    def _sanitize_name(self, name):
        """Sanitize name for Maya (replace spaces/special chars)"""
        # Replace spaces and special characters with underscores
        sanitized = re.sub(r'[^a-zA-Z0-9_]', '_', name)
        # Ensure doesn't start with number
        if sanitized and sanitized[0].isdigit():
            sanitized = f"obj_{sanitized}"
        return sanitized or "unnamed"

    def _mel_escape_string(self, s):
        """Escape string for MEL (handle backslashes, quotes)"""
        if s is None:
            return ""
        # Replace backslashes with forward slashes (Maya path convention)
        s = str(s).replace('\\', '/')
        # Escape double quotes
        s = s.replace('"', '\\"')
        return s
