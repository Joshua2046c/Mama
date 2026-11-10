# recovery_step: exact solid 1 from STEP SHA256 5ace57df0fda9a15847270cbe66048984c366595415927b0751c0765d7b14559.
# Embedded analytic topology preserves curved surfaces and avoids a duplicate published import.
from io import BytesIO
import base64, zlib, hashlib
from OCP.BRepTools import BRepTools
from OCP.BRep import BRep_Builder
from OCP.TopoDS import TopoDS_Shape

_raw_brep=zlib.decompress(base64.b64decode(_encoded_brep))
assert hashlib.sha256(_raw_brep).hexdigest()=="8e370b4c1ebb51b0a0fe3e35457ddad1998467da301a0a0a599b680c3e885050"
_wrapped=TopoDS_Shape()
BRepTools.Read_s(_wrapped,BytesIO(_raw_brep),BRep_Builder())
source=Solid(_wrapped)
assert source.is_valid and len(source.solids())==1
pocket_d=param("body_magnet_pocket_diameter",7.1)
pocket_depth=param("body_magnet_pocket_depth",1.1)
magnet_y=param("body_magnet_center_offset",23.0)
# Imported geometry is fixed evidence; patch the original 7.26 x 1.26 blind pocket.
original_y=23.0
mouth=2.5
original_floor=3.76
plug=Pos(0,original_y,mouth)*Cylinder(3.68,original_floor-mouth+0.02,align=(Align.CENTER,Align.CENTER,Align.MIN))
bore=Pos(0,magnet_y,mouth-0.02)*Cylinder(pocket_d/2,pocket_depth+0.02,align=(Align.CENTER,Align.CENTER,Align.MIN))
from build123d import SkipClean
with SkipClean():
    shell=source+plug
    shell=shell-bore
assert len(shell.solids())==1 and shell.is_valid
assert 5.6-mouth-pocket_depth>=1.9
usb_port_width=param("body_usb_access_width",13.5)
usb_port_height=param("body_usb_access_height",9.5)
usb_port_y=param("body_usb_access_center_y",-41.6)
usb_opening=Pos(0,usb_port_y,-0.1)*extrude(RectangleRounded(usb_port_width,usb_port_height,1.0),5.9)
with SkipClean():
    shell=shell-usb_opening
assert shell.is_valid and len(shell.solids())==1

# Nonthreaded PCB locators, derived from the authored carrier's four 2.5mm NPTH holes.
# Hole coordinates are fixed board interfaces: progress/source/main.tsx.
PCB_HOLES=[(-35.0,-80.0),(35.0,-80.0),(-35.0,53.0),(35.0,53.0)]
FLOOR_Z=5.6  # read back from the committed shell at all six support sites
pcb_back_z=param("body_pcb_back_z",22.8)
glue_budget=param("body_pcb_adhesive_thickness",0.1)
post_d=param("body_pcb_post_diameter",6.0)
post_root_d=param("body_pcb_root_diameter",8.0)
contact_d=param("body_pcb_contact_diameter",4.4)
pin_d=param("body_pcb_pin_diameter",2.1)
pin_h=param("body_pcb_pin_height",1.4)
post_top=pcb_back_z-glue_budget
root_h=1.5
contact_h=0.3
lead_h=0.3
supports=[]
for x,y in PCB_HOLES:
    p=Pos(x,y,FLOOR_Z-0.01)*Cylinder(post_d/2,post_top-contact_h-(FLOOR_Z-0.01),align=(Align.CENTER,Align.CENTER,Align.MIN))
    p=p.fuse(Pos(x,y,FLOOR_Z-0.01)*Cone(post_root_d/2,post_d/2,root_h,align=(Align.CENTER,Align.CENTER,Align.MIN)))
    p=p.fuse(Pos(x,y,post_top-contact_h)*Cylinder(contact_d/2,contact_h,align=(Align.CENTER,Align.CENTER,Align.MIN)))
    p=p.fuse(Pos(x,y,post_top)*Cylinder(pin_d/2,pin_h-lead_h,align=(Align.CENTER,Align.CENTER,Align.MIN)))
    p=p.fuse(Pos(x,y,post_top+pin_h-lead_h)*Cone(pin_d/2,pin_d/2-0.2,lead_h,align=(Align.CENTER,Align.CENTER,Align.MIN)))
    supports.append(p)
# Provisional edge guides for the authored 22x16x1.6mm perpendicular USB-C board.
# Only its bare outer 0.7mm strips enter the grooves; actual components need release-STEP review.
POWER_W=22.0
POWER_H=16.0
POWER_T=1.6
power_slot_gap=param("body_power_slot_clearance",0.3)
power_side_gap=param("body_power_side_clearance",0.2)
power_grip=param("body_power_edge_grip",0.7)
power_wall=param("body_power_guide_wall",2.2)
power_bottom_gap=param("body_power_bottom_gap",0.2)
power_top_extension=param("body_power_top_extension",0.5)
power_y=usb_port_y+POWER_T/2
power_bottom=FLOOR_Z+power_bottom_gap
power_top=power_bottom+POWER_H
slot_t=POWER_T+power_slot_gap
guide_depth=slot_t+2*power_wall
inner_x=POWER_W/2-power_grip
back_x=POWER_W/2+power_side_gap
outer_x=back_x+power_wall
guide_width=outer_x-inner_x
guide_top=power_top+power_top_extension
for sign in [-1,1]:
    guide=Pos(sign*(outer_x+inner_x)/2,power_y,FLOOR_Z-0.01)*extrude(RectangleRounded(guide_width,guide_depth,0.6),guide_top-(FLOOR_Z-0.01))
    slot=Pos(sign*(back_x+inner_x-0.02)/2,power_y,power_bottom)*Box(back_x-inner_x+0.02,slot_t,guide_top-power_bottom+0.02,align=(Align.CENTER,Align.CENTER,Align.MIN))
    guide=guide.cut(slot)
    supports.append(guide)
shell=shell.fuse(*supports)
assert shell.is_valid and len(shell.solids())==1
assert contact_d/2<=2.25 and pin_d<2.5
assert guide_top<pcb_back_z and post_top+pin_h<26.0
print("PCB seats",PCB_HOLES,"back_z",pcb_back_z,"pin_d",pin_d,"pad_z",post_top)
print("power_board_reservation",POWER_W,POWER_H,POWER_T,"y",power_y,"bottom/top",power_bottom,power_top,"slot",slot_t)
shell.color=srgb("#B6B8BB")
publish("body",shell,"钟壳",material="petg")
