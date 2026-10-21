
import math
j=part("body")
bd=part("base")
side=param("rail_side",-1.0)
lead=param("rail_entry_chamfer",0.2)
# Part origin is the lower stop, centered on its glue pad.
def profile(width,z0,z1):
    length=j.slide_length
    with BuildPart() as shape:
        with BuildSketch(Plane.YZ):
            with BuildLine():
                Polyline((0,z0),(length-j.top_slope*z0,z0),(length-j.top_slope*z1,z1),(0,z1),close=True)
            make_face()
        extrude(amount=width/2,both=True)
    return shape.part
pad=profile(j.bond_width,j.bond_embed-j.bond_t,j.bond_embed)
pad_edges=[e for e in pad.edges() if abs(e.center().Y)<1e-7 and abs(abs(e.center().X)-j.bond_width/2)<1e-7]
assert len(pad_edges)==2
pad=fillet(pad_edges,radius=bd.pad_corner-j.slide_gap)
rail=pad
rail+=profile(j.slide_stem,-j.slide_neck,j.bond_embed-j.bond_t+0.05)
rail+=profile(j.slide_head,-j.slide_projection,-j.slide_neck)
front_edges=[e for e in rail.edges() if abs(e.center().Y)<1e-7 and abs(e.center().Z+j.slide_projection)<1e-7 and e.length>0.5]
if front_edges: rail=chamfer(front_edges,length=lead)
assert len(rail.solids())==1
assert rail.is_valid
# Verify the sloped end is level with the assembled base's horizontal top.
cap_points=[(j.slide_top-j.top_slope*z,z) for z in (-j.slide_projection,j.bond_embed)]
base_frame=Rot(74,0,0)*Pos(0,162.12426683702384,44.101976930719864)
zs=[math.sin(math.radians(74))*(y+162.12426683702384)+math.cos(math.radians(74))*(z+44.101976930719864) for y,z in cap_points]
assert max(zs)-min(zs)<1e-6, zs
print("Bonded rail length at back plane:",j.slide_length,"mm; assembled end heights:",zs)

# Exact local checks bound the ENTIRE rail; remote shell faces cannot meet it.
aligned_body=Rot(j.tilt,0,0)*j.body
mounted_rail=Pos(side*j.slide_x,j.slide_bottom,0)*rail
rb=mounted_rail.bounding_box()
probe=Pos(rb.min.X-0.5,rb.min.Y-0.5,rb.min.Z-0.5)*Box(rb.size.X+1,rb.size.Y+1,rb.size.Z+1,align=(Align.MIN,Align.MIN,Align.MIN))
local_shell=aligned_body & probe
glue_gap=local_shell.distance_to(mounted_rail)
common=local_shell & mounted_rail
assert (not common or abs(common.volume)<1e-6), ("rail/shell overlap",common.volume)
assert glue_gap>=0.049, ("glue gap",glue_gap)
bd=part("base")
clock_base=bd.base_to_clock*bd.shell
sliding_probe=Pos(side*j.slide_x,j.slide_bottom+0.5,-j.slide_projection-1)*Box(j.bond_width+2*j.slide_gap+2,j.slide_length+2,j.slide_projection+1.2,align=(Align.CENTER,Align.MIN,Align.MIN))
local_rail=mounted_rail & sliding_probe
local_base=clock_base & sliding_probe
slide_clearance=local_rail.distance_to(local_base)
assert slide_clearance>=0.1-1e-6, ("actual sliding clearance",slide_clearance)
print("Exact full rail/shell glue gap:",glue_gap,"mm; exact moving-profile gap:",slide_clearance,"mm")

rail.color=srgb("#F5A313")
publish("rail_left",rail,"Left bonded slide",material="petg")
