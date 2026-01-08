================================================================================
ALEMBIC TO AFTER EFFECTS JSX CONVERTER
User Guide Version 1.0.0-beta.1
================================================================================

WHAT IS THIS?
-------------
This tool converts Alembic (.abc) animation files into After Effects scripts
(.jsx) that you can run in Adobe After Effects 2025.

It exports:
  • Animated cameras (with focal length and aperture)
  • Geometry transforms (as 3D nulls)
  • Locators/transforms (as 3D nulls)

================================================================================

INSTALLATION
------------
1. Download and install Visual C++ Redistributable https://aka.ms/vs/17/release/vc_redist.x64.exe

2. Save AlembicToJSX.exe anywhere on your computer
3. That's it! No installation needed.

================================================================================

HOW TO USE
----------
1. Double-click AlembicToJSX.exe

2. Click "Browse" next to "Input Alembic File"
   → Select your .abc file (from Maya, Houdini, Blender, etc.)

3. Click "Browse" next to "Output JSX File"
   → Choose where to save the .jsx file

4. Configure your composition settings:
   • Composition Name: Name for your AE comp
   • Frame Rate: Reads settings from alembic file
   • Duration: Read duration from alembic

5. Click "Convert to JSX"
   → Watch the progress log
   → Wait for "Conversion complete!" message

6. In After Effects:
   • Go to: File > Scripts > Run Script File
   • Select your generated .jsx file
   • Your scene will be imported with all animation!
   • In the next version, I'll try to include the footage as well.

================================================================================

COORDINATE SYSTEM
-----------------
  • Input: Y-up (standard in 3D apps)
  • Output: Y-up maintained in After Effects
  • Scale: 1:1 (no conversion)

Your scene should look exactly as it did in your 3D software!

================================================================================

VERSION INFORMATION
-------------------
Alembic: 1.8.10
After Effects: 2025.x (24.x+)
Coordinate System: Y-up
Scale: 1:1


