
j=part("body")
cover_thickness=param("cover_thickness",2.2)
notch_width=param("cover_finger_notch_width",15.0)
notch_height=param("cover_finger_notch_height",2.0)
cover=extrude(RectangleRounded(j.hatch_size,j.hatch_size,j.hatch_r),amount=cover_thickness)
for x,y in j.magnet_centers:
    pocket=Pos(x,y,cover_thickness-j.magnet_pocket_depth)*Cylinder(j.magnet_pocket_d/2,j.magnet_pocket_depth+0.1,align=(Align.CENTER,Align.CENTER,Align.MIN))
    cover-=pocket
notch=Pos(0,-j.hatch_size/2-1,-1)*Box(notch_width,notch_height+1,cover_thickness+2,align=(Align.CENTER,Align.MIN,Align.MIN))
cover-=notch
# The local circular pocket floor is 0.94 mm with the requested 1.26 mm depth.
assert cover_thickness-j.magnet_pocket_depth>=0.9-1e-8
assert len(cover.solids())==1
assert cover.is_valid
cover.color=srgb("#F5A313")
publish("battery_cover",cover,"Magnetic battery cover",material="petg")