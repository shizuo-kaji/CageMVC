Cage deformer plugin for Maya based on Mean Value Coordinates
=============
/**
 * @brief Cage deformer plugin for Maya based on Mean Value Coordinates
 * @section LICENSE The MIT License
 * @section requirements: 
 * @section Autodesk Maya: http://www.autodesk.com/products/autodesk-maya/overview
 * @section numpy
 * @version 0.10
 * @author Shizuo KAJI
 */

How to use:
1. Place the plugin file in "MAYA_PLUG_IN_PATH"
2. Load the plugin from "Plugin Manager"
3. Select a target mesh
4. Open Script editor in Maya and type in the following Python command:

        import maya.cmds as cmds
        deformer = cmds.deformer(type='cageDeformerMVC')[0]

5. Then, select a cage mesh and type the following:

       shape=pm.selected( type="transform" )[0].getShapes()[0]
       cmds.connectAttr(shape+".outMesh", deformer+".cageMesh")

6. Wait for a moment, and edit the cage mesh
