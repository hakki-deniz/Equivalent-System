"""
    This piece of code is prepared for the question at:

        https://portwooddigital.com/2022/05/01/a-complicated-equivalent/

    ---
    This script is a representative of "three-point Gauss-Legendre" model.

    The code creates a cantilever column model with four rigid elements and
    three zeroLength elements.

    The flexural rigidity of the zeroLength elements that gives the correct
    lateral displacement, are calculated via "virtual work method".

    ---
    
"""

import openseespy.opensees as ops

##########
## Create a cantilaver column model with rotational springs
##########

## The model is unitless!

ops.wipe()

# Create a Model
ops.model("basic","-ndm",2,"-ndf",3)

L = 100

zeroL_locations = [0.2,0.5,0.8] #zeroLength element relative locations

## Set nodes
ops.node(1,0.0, 0.0)
ops.node(2,0.0, L*zeroL_locations[0])
ops.node(3,0.0, L*zeroL_locations[1])
ops.node(4,0.0, L*zeroL_locations[2])
ops.node(5,0.0, L)


## Set nodes for zeroLength elements
ops.node(22,0.0, L*zeroL_locations[0])
ops.node(33,0.0, L*zeroL_locations[1])
ops.node(44,0.0, L*zeroL_locations[2])


## Define boundary Conditions
ops.fix(1, 1, 1, 1)

## Define constraints for ZeroLength elements
ops.equalDOF(2,22,1,2)
ops.equalDOF(3,33,1,2)
ops.equalDOF(4,44,1,2)


## Define elements
## Rigid Elements
tag_el = 1

Es = 200000  
I_sec = 1e+07 #For rigid section
A = 1e+9

ops.geomTransf('Linear', tag_el)

ops.element('elasticBeamColumn', 1, 1, 2, A, Es, I_sec, tag_el)
ops.element('elasticBeamColumn', 2, 22, 3, A, Es, I_sec, tag_el)
ops.element('elasticBeamColumn', 3, 33, 4, A, Es, I_sec, tag_el)
ops.element('elasticBeamColumn', 4, 44, 5, A, Es, I_sec, tag_el)


## zeroLength elements
## Define material
mat_zL = 2 #For zeroLength elements

I_init = 10000 #Initial I

#########
#### <<< The ANSWER for the stiffness value >>>
#########

#I_mod = I_init #Modified I for Answer A
#I_mod = I_init/L #Modified I for Answer B
#I_mod = 3*I_init/L #Modified I for Answer C
I_mod = 278.9944201 #Answer obtained by using virtual work method
#########

ops.uniaxialMaterial('Elastic', mat_zL, I_mod*Es)

ops.element('zeroLength', 10, 2, 22, '-mat', mat_zL, '-dir', 6) #6 for the rotation about z-axis
ops.element('zeroLength', 11, 3, 33, '-mat', mat_zL, '-dir', 6)
ops.element('zeroLength', 12, 44, 4, '-mat', mat_zL, '-dir', 6)

## Define load
ops.timeSeries('Constant',1)
ops.pattern('Plain',1,1)

P_ = 1000
ops.load(5, P_, 0.0, 0.0) #Lateral load assigned to the top of the column

## Define analysis parameters
ops.system("ProfileSPD")
ops.numberer("Plain")
ops.constraints("Plain")
ops.integrator("LoadControl", 1)
ops.algorithm("Newton")
ops.analysis('Static')
ops.analyze(10)

## Get lateral displacement of the model
lat_def_analyzed = ops.nodeDisp(5,1)

## The exact solution
lat_def_calculated = (P_*(L**3))/(3*Es*I_init)

rel_error = abs(100*(lat_def_calculated-lat_def_analyzed) / lat_def_calculated) #Error ratio

## Print the results and difference
print("Lateral displacements:")
print(f"    Analyzed: {lat_def_analyzed:.5f} | Calculated: {lat_def_calculated:.5f}")
print(f"    Relative error : {rel_error:.2f}%")
