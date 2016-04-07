# -*- coding: utf-8 -*-
  
# Cage deformer for Maya based on Mean value coordinates
# 
#  @author      Shizuo KAJI
#  @date        2013/5/13

# usage:
#   Load the plugin from "Plugin Manager"
#   Select a target mesh and type the following from the script editor:
#        import maya.cmds as cmds
#        deformer = cmds.deformer(type='cageDeformerMVC')[0]
#   Then, select a cage mesh and type the following:
#        shape=pm.selected( type="transform" )[0].getShapes()[0]
#        cmds.connectAttr(shape+".outMesh", deformer+".cageMesh")
#   Wait for a moment, and edit the cage mesh

import maya.OpenMayaMPx as OpenMayaMPx
import maya.OpenMaya as OpenMaya
import numpy as np

OFF = 10
ON = 0

class CageDeformerNode(OpenMayaMPx.MPxDeformerNode):
    kPluginNodeId = OpenMaya.MTypeId(0x000000020)
    kPluginNodeName = 'cageDeformerMVC'
     
    aCageMesh = OpenMaya.MObject()

    w=[]   # weights
    p=[]   # vertices of the cage
    
    def __init__(self):
        OpenMayaMPx.MPxDeformerNode.__init__(self)
 
    def deform(self, data, itGeo, localToWorldMatrix, mIndex):
        blendMode = data.inputValue( CageDeformerNode.aBlendMode ).asShort()
        if blendMode == OFF:
            self._resetPosition(itGeo)
            return
        CageMesh = data.inputValue(CageDeformerNode.aCageMesh).asMesh()
        if CageMesh.isNull():
            return
        cageMesh = OpenMaya.MFnMesh(CageMesh)
        q=self._getPoints(cageMesh)
        if len(self.p)!= len(q):
            # initialisation
            self.p=q
            tri=self._getTri(cageMesh)
            self.w=[]
            while not itGeo.isDone():
                mu=np.zeros(len(q))
                pt = itGeo.position()
                v = np.array([pt.x, pt.y, pt.z])
                for tr in tri:
                    e=[v-q[tr[i]] for i in range(3)]
                    en=[e[i]/np.linalg.norm(e[i]) for i in range(3)] 
                    b=[np.arccos(np.dot(en[(i+1)%3],en[(i+2)%3])) for i in range(3)]
                    n=[np.cross(en[(i+1)%3],en[(i+2)%3]) for i in range(3)]
                    nu=[n[i]/np.linalg.norm(n[i]) for i in range(3)] 
                    a=[np.dot(nu[(i+1)%3],nu[(i+2)%3]) for i in range(3)]
                    for i in range(3):
                        mu[tr[i]]-=(b[i]+b[(i+2)%3]*a[(i+1)%3]+b[(i+1)%3]*a[(i+2)%3])/(2.0*np.dot(en[i],nu[i]))
                mu /= np.array([np.linalg.norm(v-q[j]) for j in range(len(q))])
                smu=sum(mu)
                self.w.append(np.array([mu[j]/smu for j in range(len(q))]))
                itGeo.next() 
            return
            
        # run-time
        pts = OpenMaya.MPointArray()
        itGeo.allPositions(pts)   
        for i in range(pts.length()):
            pos = sum([self.w[i][j]*q[j] for j in range(len(q))])
            pts[i].x, pts[i].y, pts[i].z=[pos[0],pos[1],pos[2]]
        itGeo.setAllPositions(pts)
        return
    

    def _resetPosition(self,itGeo):
        while not itGeo.isDone():
            pt = itGeo.position()
            itGeo.setPosition(pt)
            itGeo.next() 
        return
    
    def _getPoints(self, mesh):
        qs = OpenMaya.MPointArray()
        mesh.getPoints(qs)
        q=[np.array( [ qs[i].x, qs[i].y, qs[i].z ]) for i in range(qs.length())]
        return q
        
    def _getTri(self, mesh):
        count = OpenMaya.MIntArray()
        tl = OpenMaya.MIntArray( )
        mesh.getTriangles(count, tl)
        num=len(tl)/3
        tri = [ (tl[3*i], tl[3*i+1], tl[3*i+2]) for i in range(num)]
        return tri

    
def creator():
    return OpenMayaMPx.asMPxPtr(CageDeformerNode())
 
def initialize():
    outputGeom = OpenMayaMPx.cvar.MPxDeformerNode_outputGeom

    tAttr = OpenMaya.MFnTypedAttribute()
    CageDeformerNode.aCageMesh = tAttr.create('cageMesh', 'cm', OpenMaya.MFnData.kMesh)
    tAttr.setStorable(False)
    CageDeformerNode.addAttribute( CageDeformerNode.aCageMesh )
    CageDeformerNode.attributeAffects(CageDeformerNode.aCageMesh, outputGeom)
      
    # interpolation mode 
    eAttr = OpenMaya.MFnEnumAttribute()
    CageDeformerNode.aBlendMode = eAttr.create( "blendMode", "bm", 0 )
    eAttr.addField( "MVC", ON )
    eAttr.addField( "off", OFF )
    eAttr.setStorable( True )
    CageDeformerNode.addAttribute( CageDeformerNode.aBlendMode)    
    CageDeformerNode.attributeAffects(CageDeformerNode.aBlendMode, outputGeom)  

def initializePlugin(obj):
    plugin = OpenMayaMPx.MFnPlugin(obj, 'Shizuo KAJI', '1.0', 'Any')
    try:
        plugin.registerNode(CageDeformerNode.kPluginNodeName, CageDeformerNode.kPluginNodeId, creator, initialize, OpenMayaMPx.MPxNode.kDeformerNode)
    except:
        raise RuntimeError, 'Failed to register node'
 
def uninitializePlugin(obj):
    plugin = OpenMayaMPx.MFnPlugin(obj)
    try:
        plugin.deregisterNode(CageDeformerNode.kPluginNodeId)
    except:
        raise RuntimeError, 'Failed to deregister node'