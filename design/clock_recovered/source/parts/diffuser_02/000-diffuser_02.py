j=part("dial")
front_gap=param("diffuser_02_front_clearance",0.2)
window=j.window_size-2*front_gap
flange_gap=param("diffuser_02_flange_clearance",0.1)
flange=j.flange_pocket_size-2*flange_gap
height=param("diffuser_02_height",2.2)
flange_h=param("diffuser_02_flange_thickness",0.8)
gap=param("diffuser_02_back_gap",0.2)
x,y=j.led_centers[1]
z=j.dial_back_z+gap
s=Pos(x,y,z)*extrude(RectangleRounded(flange,flange,0.4),flange_h)
s=s+Pos(x,y,z+flange_h-0.01)*extrude(RectangleRounded(window,window,0.35),height-flange_h+0.01)
s.color=srgb("#EEECE4")
assert len(s.solids())==1 and s.is_valid
publish("diffuser_02",s,"扩散窗 2",material="petg")
