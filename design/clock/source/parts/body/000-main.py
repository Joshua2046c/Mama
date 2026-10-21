dia=param("body_diameter",240.0)
depth=param("body_depth",32.0)
wall=param("body_wall",2.7)
back=param("body_back_thickness",3.5)
seat_z=param("body_seat_height",25.8)
seat_thick=param("body_seat_thickness",2.8)
seat_width=param("body_seat_width",5.3)
# Legacy parameter ids retained; these dimensions now drive true tangent radii.
rear_bevel=param("body_rear_chamfer",7.0)
front_bevel=param("body_front_chamfer",1.0)
mouth_radius=param("body_inner_lip_radius",0.8)
tilt=param("body_tilt_angle",8.0)
r=dia/2
blank=Cylinder(r,depth,align=(Align.CENTER,Align.CENTER,Align.MIN))
rear_edges=[e for e in blank.edges() if e.geom_type==GeomType.CIRCLE and abs(e.center().Z)<1e-6]
blank=fillet(rear_edges,radius=rear_bevel)
front_edges=[e for e in blank.edges() if e.geom_type==GeomType.CIRCLE and abs(e.center().Z-depth)<1e-6]
blank=fillet(front_edges,radius=front_bevel)
inner_r=r-wall
inner_start=r-rear_bevel-back
ramp=inner_r-inner_start
cavity=Pos(0,0,back)*Cone(inner_start,inner_r,ramp,align=(Align.CENTER,Align.CENTER,Align.MIN))
cavity=cavity+Pos(0,0,back+ramp)*Cylinder(inner_r,depth,align=(Align.CENTER,Align.CENTER,Align.MIN))
shell=blank-cavity
mouth_edges=[e for e in shell.edges() if e.geom_type==GeomType.CIRCLE and abs(e.center().Z-depth)<1e-6 and abs(e.radius-inner_r)<1e-6]
assert len(mouth_edges)==1
shell=fillet(mouth_edges,radius=mouth_radius)
# Fully supported annular dial seat: no suspended shelf or underside recess.
# Preserve the existing seat top/radius and nested-dial position.
assert seat_z-back>=seat_thick
ledge=Pos(0,0,back)*extrude(Circle(inner_r)-Circle(inner_r-seat_width),amount=seat_z-back)


# Shared removable-cover and bonded-slider interfaces.
hatch_size=param("body_hatch_size",58.0)
hatch_r=param("body_hatch_radius",3.0)
hatch_gap=param("body_hatch_gap",0.3)
door_t=param("body_door_thickness",2.2)
seat_depth=param("body_hatch_seat_depth",2.5)
hatch_ledge=param("body_hatch_ledge",1.5)
magnet_d=param("body_magnet_diameter",7.0)
magnet_t=param("body_magnet_thickness",1.0)
magnet_pocket_d=param("body_magnet_pocket_diameter",7.1)
magnet_pocket_depth=param("body_magnet_pocket_depth",1.1)
magnet_d_gap=magnet_pocket_d-magnet_d
magnet_bed=magnet_pocket_depth-magnet_t
magnet_xy=param("body_magnet_center_offset",23.0)
magnet_boss_size=param("body_magnet_boss_size",11.0)
magnet_boss_z=param("body_magnet_boss_inner_z",5.6)
magnet_boss_r=param("body_magnet_boss_radius",2.0)
slide_x=param("body_slide_spacing_half",35.0)
slide_bottom=param("body_slide_bottom",-47.0)
# Existing assembled base top: (160 - 168) / cos(16 degrees).
slide_top=param("body_slide_top_y",-8.322395486893)
slide_length=slide_top-slide_bottom
slide_stem=param("body_slide_stem_width",4.5)
slide_head=param("body_slide_head_width",8.0)
slide_neck=param("body_slide_neck_depth",2.5)
slide_projection=param("body_slide_projection",5.0)
slide_gap=param("body_slide_clearance",0.25)
bond_width=param("body_rail_bond_width",10.0)
bond_t=param("body_rail_bond_thickness",0.85)
bond_embed=param("body_rail_bond_embed",0.05)
bond_recess=param("body_rail_recess_depth",0.1)
bond_loc_gap=param("body_rail_recess_side_gap",0.1)
bond_corner=param("body_rail_bond_corner_radius",2.0)
detent_length=param("body_slide_detent_arm_length",9.0)
detent_t=param("body_slide_detent_arm_thickness",1.0)
detent_width=param("body_slide_detent_arm_width",2.8)
detent_slit=param("body_slide_detent_slit",0.6)
detent_rise=param("body_slide_detent_rise",0.55)
hanger_y=param("body_hanger_y",86.0)
hanger_entry=param("body_hanger_entry_diameter",9.0)
hanger_neck=param("body_hanger_neck_width",3.8)
hanger_rise=param("body_hanger_neck_rise",10.0)
min_cavity=param("body_minimum_cavity_depth",17.0)
import math
top_slope=math.tan(math.radians(tilt))
opening_size=hatch_size+2*hatch_gap
body=shell+ledge
outer_cut=Pos(0,0,-1)*extrude(RectangleRounded(opening_size,opening_size,hatch_r+hatch_gap),amount=seat_depth+1)
inner_size=opening_size-2*hatch_ledge
inner_cut=Pos(0,0,-1)*extrude(RectangleRounded(inner_size,inner_size,max(hatch_r+hatch_gap-hatch_ledge,0.5)),amount=back+2)
body=body-outer_cut-inner_cut
magnet_centers=[(0,magnet_xy)]
for x,y in magnet_centers:
    tab_bottom=y-magnet_boss_size/2
    tab_top=opening_size/2+hatch_ledge
    tab=Pos(x,(tab_bottom+tab_top)/2,seat_depth)*extrude(RectangleRounded(magnet_boss_size,tab_top-tab_bottom,magnet_boss_r),amount=magnet_boss_z-seat_depth)
    body+=tab
    pocket=Pos(x,y,seat_depth-0.1)*Cylinder(magnet_pocket_d/2,magnet_pocket_depth+0.1,align=(Align.CENTER,Align.CENTER,Align.MIN))
    body-=pocket
# No integrated rails: only 0.1 mm deep glue-positioning recesses.
rail_recess_top=slide_top+top_slope*(bond_t-bond_embed)+bond_loc_gap
for x in (-slide_x,slide_x):
    recess=Pos(x,slide_bottom-bond_loc_gap,-0.1)*Box(bond_width+2*bond_loc_gap,rail_recess_top-slide_bottom+bond_loc_gap,bond_recess+0.1,align=(Align.CENTER,Align.MIN,Align.MIN))
    recess_edges=[e for e in recess.edges() if abs(e.center().Y-(slide_bottom-bond_loc_gap))<1e-7 and abs(abs(e.center().X-x)-(bond_width/2+bond_loc_gap))<1e-7]
    assert len(recess_edges)==2
    recess=fillet(recess_edges,radius=bond_corner+bond_loc_gap)
    body-=recess
# Rear keyhole retained, centered above the clock axis.
hanger=Pos(0,hanger_y,-1)*Cylinder(hanger_entry/2,back+2,align=(Align.CENTER,Align.CENTER,Align.MIN))
hanger+=Pos(0,hanger_y+hanger_rise/2,-1)*Box(hanger_neck,hanger_rise,back+2,align=(Align.CENTER,Align.CENTER,Align.MIN))
hanger+=Pos(0,hanger_y+hanger_rise,-1)*Cylinder(hanger_neck/2,back+2,align=(Align.CENTER,Align.CENTER,Align.MIN))
body-=hanger
# Internal nail-head recess, half the actual backplate thickness deep.
hanger_relief_w=param("body_hanger_relief_width",16.0)
hanger_relief_h=param("body_hanger_relief_height",26.0)
hanger_relief_r=param("body_hanger_relief_radius",3.0)
hanger_relief_y=hanger_y+(hanger_rise+hanger_neck/2-hanger_entry/2)/2
hanger_relief_depth=back/2
hanger_relief_floor=back-hanger_relief_depth
hanger_relief=Pos(0,hanger_relief_y,hanger_relief_floor)*extrude(RectangleRounded(hanger_relief_w,hanger_relief_h,hanger_relief_r),amount=hanger_relief_depth+0.1)
body-=hanger_relief
assert abs(hanger_relief.bounding_box().min.Z-back/2)<1e-7
assert hanger_relief_w>=hanger_entry+4
assert hanger_relief_h>=hanger_rise+hanger_neck/2+hanger_entry/2+4
assert hanger_relief_floor>=2
movement_clear_depth=26.0-max(back,magnet_boss_z)
assert movement_clear_depth>=min_cavity
assert abs(bond_recess-0.1)<1e-8
assert slide_gap>=0.1
# Local magnet-pocket floor remains solid after the user requested deeper pockets.
assert magnet_boss_z-seat_depth-magnet_pocket_depth>=1.8-1e-8
assert abs(magnet_boss_z-back)<1e-8, ("magnet support must be flush with inside back",magnet_boss_z,back)
assert abs(tab.bounding_box().max.Z-back)<1e-8
assert len(body.solids())==1
print("Minimum movement depth including magnet tabs:",movement_clear_depth,"mm; rail locating recess:",bond_recess,"mm")
# Four independent front-dial magnet pairs, separate from the battery-cover pair.
dial_magnet_d=param("body_dial_magnet_pocket_diameter",7.1)
dial_magnet_depth=param("body_dial_magnet_pocket_depth",1.1)
dial_magnet_radius=param("body_dial_magnet_radius",112.5)
dial_magnet_margin=param("body_dial_magnet_seat_wall",2.0)
dial_magnet_centers=[(0,dial_magnet_radius),(dial_magnet_radius,0),(0,-dial_magnet_radius),(-dial_magnet_radius,0)]
dial_magnet_bore_tools=[]
for x,y in dial_magnet_centers:
    support=Pos(x,y,back)*Cylinder(dial_magnet_d/2+dial_magnet_margin,seat_z-back,align=(Align.CENTER,Align.CENTER,Align.MIN))
    outside=support-blank
    assert not outside or abs(outside.volume)<1e-6
    body+=support
    bore=Pos(x,y,seat_z-dial_magnet_depth)*Cylinder(dial_magnet_d/2,dial_magnet_depth+0.1,align=(Align.CENTER,Align.CENTER,Align.MIN))
    body-=bore
    dial_magnet_bore_tools.append(bore)
assert len(dial_magnet_bore_tools)==4
assert seat_z-dial_magnet_depth-back>=2
assert dial_magnet_radius-dial_magnet_d/2-dial_magnet_margin>hanger_relief_y+hanger_relief_h/2
assert len(body.solids())==1
body=Rot(-tilt,0,0)*body
# Exact analytic surface partition for portable smooth meshing.
# 3 degree patches retain the same circular surfaces and G1 tangent joins.
# This bounds a possible perimeter chord sag to 0.042 mm at radius 120 mm.
import math
from OCP.ShapeUpgrade import ShapeUpgrade_ShapeDivideAngle
from OCP.BRepGProp import BRepGProp
from OCP.GProp import GProp_GProps
def precise_volume(shape):
    props=GProp_GProps()
    BRepGProp.VolumeProperties_s(shape.wrapped,props,1e-9)
    return props.Mass()
_before_volume=precise_volume(body)
divider=ShapeUpgrade_ShapeDivideAngle(math.radians(3.0),body.wrapped)
divider.Perform()
body=Part(divider.Result())
# Preserve only the large circular preview divisions. Hinge bores stay single
# analytic cylinders, avoiding expensive near-coincident patch distance tests.
from OCP.ShapeUpgrade import ShapeUpgrade_UnifySameDomain
unifier=ShapeUpgrade_UnifySameDomain(body.wrapped,True,True,False)
# Keep angular subdivisions only on the large concentric casing surfaces.
# Small magnet cylinders remain analytic single faces after unification.
from OCP.BRepAdaptor import BRepAdaptor_Surface
from OCP.GeomAbs import GeomAbs_Cylinder, GeomAbs_Cone, GeomAbs_Torus
for face in body.faces():
    surf=BRepAdaptor_Surface(face.wrapped)
    typ=surf.GetType()
    large=False
    if typ==GeomAbs_Cylinder: large=surf.Cylinder().Radius()>90
    elif typ==GeomAbs_Cone: large=surf.Cone().RefRadius()>90
    elif typ==GeomAbs_Torus: large=surf.Torus().MajorRadius()>90
    if large:
        for edge in face.edges(): unifier.KeepShape(edge.wrapped)
unifier.Build()
body=Part(unifier.Shape())
print("Body analytic face count:",len(body.faces()))
assert len(body.solids())==1
assert abs(precise_volume(body)-_before_volume)<0.001, (precise_volume(body),_before_volume)
body.color=Color(0.94,0.53,0.025)
assert len(body.solids())==1
publish("body",body,"Recessed clock body",material="petg")