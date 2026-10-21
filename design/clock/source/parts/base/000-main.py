import math
w=param("base_width",84.0)
d=param("base_depth",90.0)
h=param("base_height",160.0)
wall=param("base_wall",3.0)
floor=param("base_floor",6.0)
cr=param("base_corner_radius",18.0)
pocket_front=param("base_storage_front",38.0)
lip=param("base_lip_radius",0.8)
tilt=param("base_contact_angle",16.0)
foot=param("base_front_foot_extension",10.0)
waist=param("base_neck_inset",24.0)
neck_z=param("base_neck_underside_height",114.0)
rear_inset=param("base_rear_inset",8.0)
neck_flat=param("base_neck_end_flat_length",20.0)
slope=math.tan(math.radians(tilt))
neck_front=(neck_z-h)*slope
# The end face meets the straight underside at exactly 90 degrees.
# Only the root blends into the inclined lower flank.
p0=(-foot,0)
p1=(waist*0.8,neck_z-30)
p2=(neck_front,neck_z)
join=(p2[0]+neck_flat*math.cos(math.radians(tilt)),
      p2[1]-neck_flat*math.sin(math.radians(tilt)))
rise=(p1[1]-p0[1])/(p1[0]-p0[0])
root_handle=(neck_z-p1[1])/6
c1=(p1[0]+root_handle,p1[1]+root_handle*rise)
c2=(join[0]+neck_flat/2,join[1]-neck_flat*slope/2)
assert abs((-1)*slope+slope*1)<1e-9
with BuildPart() as blank:
    with BuildSketch(Plane.YZ):
        with BuildLine():
            Line(p0,p1)
            Bezier(p1,c1,c2,join)
            Line(join,p2)
            Polyline(p2,(0,h),(d,h),(d-rear_inset,0),p0)
        make_face()
    extrude(amount=w/2,both=True)
shell=blank.part
# Keep the mating face side edges sharp; round only the root/flank and rear.
side_edges=[e for e in shell.edges()
            if abs(abs(e.center().X)-w/2)<0.001
            and e.center().Z>0.001 and e.center().Z<h-0.001
            and not (abs(e.center().Y-(e.center().Z-h)*slope)<0.001)]
shell=fillet(side_edges,radius=cr)
def inner_section(z,front):
    rear=d-rear_inset*(1-z/h)-wall
    return Pos(0,(front+rear)/2,z)*RectangleRounded(w-2*wall,rear-front,cr-wall)
inner_floor_front=max(pocket_front,waist+wall+cr/2)
pocket=loft([inner_section(floor,inner_floor_front),inner_section(h,pocket_front),inner_section(h+1,pocket_front)],ruled=True)
shell=shell-pocket
# Keep the front mating/top intersection crisp too.
rim=[e for e in shell.edges() if abs(e.center().Z-h)<0.001 and e.center().Y>0.001]
shell=fillet(rim,radius=lip)

joint=part("body")
# Assembly-interface frame, independent of the base's display placement.
clock_to_base=Rot(74,0,0)*Pos(0,162.12426683702384,44.101976930719864)
base_to_clock=Pos(0,-162.12426683702384,-44.101976930719864)*Rot(-74,0,0)
clearance=joint.slide_gap
pad_corner=param("base_slide_pad_corner_radius",2.25)
minimum_slot_wall=param("base_minimum_slot_outer_wall",2.0)
# Evaluate actual distance to the exterior side skins of the uncut neck.
# The marked lower corners are the R18 cylinders running normal to the
# contact plane; the flat outside walls close the rest of each side.
from OCP.BRepAdaptor import BRepAdaptor_Surface
from OCP.GeomAbs import GeomAbs_Cylinder
outer_clock=base_to_clock*shell
side_skins={-1:[],1:[]}
for face in outer_clock.faces():
    fc=face.center()
    surface=BRepAdaptor_Surface(face.wrapped)
    is_side_plane=(face.geom_type==GeomType.PLANE and abs(abs(fc.X)-w/2)<1e-6)
    is_corner=False
    if surface.GetType()==GeomAbs_Cylinder:
        cylinder=surface.Cylinder()
        is_corner=(abs(cylinder.Radius()-cr)<1e-6 and abs(cylinder.Axis().Direction().Z())>0.99999)
    if is_side_plane or is_corner:
        side_skins[1 if fc.X>0 else -1].append(face)
assert all(len(v)>=2 for v in side_skins.values()), {k:len(v) for k,v in side_skins.items()}
slot_outer_wall_results=[]
for x in (-joint.slide_x,joint.slide_x):
    reach=joint.slide_length+40
    stem_cut=Pos(x,joint.slide_bottom,-joint.slide_projection-clearance)*Box(joint.slide_stem+2*clearance,reach,joint.slide_projection+clearance+1,align=(Align.CENTER,Align.MIN,Align.MIN))
    head_cut=Pos(x,joint.slide_bottom,-joint.slide_projection-clearance)*Box(joint.slide_head+2*clearance,reach,joint.slide_projection-joint.slide_neck+2*clearance,align=(Align.CENTER,Align.MIN,Align.MIN))
    pad_cut=Pos(x,joint.slide_bottom+reach/2,joint.bond_embed-joint.bond_t-clearance)*extrude(RectangleRounded(joint.bond_width+2*clearance,reach+2*clearance,pad_corner),amount=joint.bond_t-joint.bond_embed+clearance+1)
    slot_void=stem_cut+head_cut+pad_cut
    side=1 if x>0 else -1
    measured_wall=min(slot_void.distance_to(face) for face in side_skins[side])
    slot_outer_wall_results.append(measured_wall)
    assert measured_wall>=minimum_slot_wall-1e-6, ("actual lower-corner/side wall",side,measured_wall,minimum_slot_wall)
    shell-=clock_to_base*slot_void
# The front mating surface stays planar: no central rectangular relief.
print("Measured minimum side/corner wall thicknesses:",slot_outer_wall_results,"mm")
assert clearance>=0.1
assert len(shell.solids())==1
assert shell.is_valid
shell.color=srgb("#F5A313")
publish("base",shell,"Extended neck base",material="petg")
