# cell: dial
# New face design replaces the recovered dial, preserving its mating dimensions.
dial_back_z=param("dial_back_height",26.0)
dial_thickness=param("dial_flat_thickness",2.4)
dial_radius=param("dial_outer_radius",117.0)
shaft_d=param("dial_shaft_hole_diameter",10.0)
lip_start=param("dial_lip_start_radius",108.0)
lip_top=param("dial_lip_top_height",30.5436)
magnet_r=param("dial_magnet_center_radius",111.0)
magnet_d=param("dial_magnet_pocket_diameter",7.1)
magnet_depth=param("dial_magnet_pocket_depth",1.1)
grid_pitch=param("dial_grid_pitch",7.0)
line_width=param("dial_grid_line_width",0.4)
led_pitch=param("dial_led_pitch",14.0)
led_lower_y=param("dial_led_lower_y",31.5)
window_size=grid_pitch-line_width  # clear cell width, measured between grid inner edges
window_radius=param("dial_light_window_radius",0.5)
flange_pocket_size=window_size+2*param("dial_diffuser_pocket_overhang",0.7)
flange_pocket_depth=param("dial_diffuser_flange_depth",1.0)
flat_top=dial_back_z+dial_thickness
led_centers=[(i*led_pitch,y) for y in [led_lower_y+led_pitch,led_lower_y] for i in [-2,-1,0,1,2]]
# Cross-section has a true R0.5 rear edge and R1 outer lip; all arcs stay analytic.
with BuildLine(Plane.XZ) as outline:
    Polyline((shaft_d/2,dial_back_z),(dial_radius-0.5,dial_back_z))
    ThreePointArc((dial_radius-0.5,dial_back_z),(dial_radius-0.1464466,dial_back_z+0.1464466),(dial_radius,dial_back_z+0.5))
    Polyline((dial_radius,dial_back_z+0.5),(dial_radius,lip_top-1))
    ThreePointArc((dial_radius,lip_top-1),(dial_radius-0.2928932,lip_top-0.2928932),(dial_radius-1,lip_top))
    ThreePointArc((dial_radius-1,lip_top),((dial_radius-1+lip_start)/2,flat_top+0.7),(lip_start,flat_top))
    Polyline((lip_start,flat_top),(shaft_d/2,flat_top),(shaft_d/2,dial_back_z))
s=revolve(make_face(outline.wires()),axis=Axis.Z)
dial_blank=s  # original curved face is retained for a constant-depth rim groove
s=s.cut(*[Pos(x,y,dial_back_z-0.01)*Cylinder(magnet_d/2,magnet_depth+0.01,align=(Align.CENTER,Align.CENTER,Align.MIN)) for x,y in [(0,magnet_r),(magnet_r,0),(0,-magnet_r),(-magnet_r,0)]])
s=s.cut(*[Pos(x,y,dial_back_z-0.01)*extrude(RectangleRounded(window_size,window_size,window_radius),dial_thickness+0.02) for x,y in led_centers])
s=s.cut(*[Pos(x,y,dial_back_z-0.01)*extrude(RectangleRounded(flange_pocket_size,flange_pocket_size,window_radius),flange_pocket_depth+0.01) for x,y in led_centers])

# All face features belong to this manufactured dial, not separate overlay parts.
grid_height=param("dial_grid_relief_height",0.1)
relief_height=param("dial_markings_relief_height",0.2)
art_radius=param("dial_art_radius",107.5)
font_size=param("dial_numeral_size",29.0)
number_radius=param("dial_numeral_radius",83.0)
tick_radius=param("dial_tick_radius",101.0)
minute_width=param("dial_minute_width",0.55)
minute_length=param("dial_minute_length",5.0)
hour_width=param("dial_hour_width",1.1)
hour_length=param("dial_hour_length",8.0)
cardinal_width=param("dial_cardinal_width",4.5)
cardinal_length=param("dial_cardinal_length",11.0)
cardinal_radius=param("dial_cardinal_radius",101.5)
logo_size=param("dial_logo_size",8.8)
logo_y=param("dial_logo_y",-41.0)
join_depth=0.02  # construction overlap only; exposed relief heights stay exact
from math import sin,cos,pi
curve_tolerance=param("dial_curve_tolerance",0.005)

def polygon_glyph_faces(text,size,tolerance):
    def flat_wire(w):
        pieces=[]
        def samples(e,a,b,pa,pb,depth):
            v=pb-pa
            vv=v.dot(v)
            ts=[a+(b-a)*q for q in [0.25,0.5,0.75]]
            ps=[e.position_at(q) for q in ts]
            deviations=[(p-(pa+v*max(0,min(1,(p-pa).dot(v)/vv)))).length if vv>1e-16 else (p-pa).length for p in ps]
            if max(deviations)<=tolerance or depth>=18:
                return [pa,pb]
            mid=(a+b)/2
            pm=ps[1]
            return samples(e,a,mid,pa,pm,depth+1)[:-1]+samples(e,mid,b,pm,pb,depth+1)
        for edge in w.order_edges():
            if edge.geom_type==GeomType.LINE:
                pieces.append(edge)
            else:
                pts=samples(edge,0,1,edge.position_at(0),edge.position_at(1),0)
                pieces.extend(Polyline(*pts).edges())
        wires=Wire.combine(pieces,tol=1e-6)
        assert len(wires)==1 and wires[0].is_closed
        return wires[0]
    original=Text(text,size,font="Arial",font_style=FontStyle.BOLD)
    return [Face(flat_wire(f.outer_wire()),[flat_wire(w) for w in f.inner_wires()]) for f in original.faces()]

# Fuse in 2D first: one connected grid profile rather than crossing 3D bars.
grid_profiles=[]
for n in range(-16,17):
    x=(n+0.5)*grid_pitch
    y=n*grid_pitch
    if abs(x)<art_radius:
        grid_profiles.append(Pos(x,0)*Rectangle(line_width,2*dial_radius))
    if abs(y)<art_radius:
        grid_profiles.append(Pos(0,y)*Rectangle(2*dial_radius,line_width))
grid_profile=grid_profiles[0].fuse(*grid_profiles[1:]).clean()
grid_profile=(grid_profile & Circle(art_radius))-Circle(shaft_d/2)
grid_relief=Pos(0,0,flat_top-join_depth)*extrude(grid_profile,grid_height+join_depth)
raised=[]
for h in range(1,13):
    a=h*pi/6
    raised.extend([Pos(number_radius*sin(a),number_radius*cos(a),flat_top-join_depth)*extrude(f,relief_height+join_depth) for f in polygon_glyph_faces(str(h),font_size,curve_tolerance)])
for n in range(60):
    cardinal=n%15==0
    w=cardinal_width if cardinal else (hour_width if n%5==0 else minute_width)
    length=cardinal_length if cardinal else (hour_length if n%5==0 else minute_length)
    radius=cardinal_radius if cardinal else tick_radius
    raised.append(Rot(0,0,-n*6)*Pos(0,radius,flat_top-join_depth)*Box(w,length,relief_height+join_depth,align=(Align.CENTER,Align.CENTER,Align.MIN)))
raised.extend([Pos(0,logo_y,flat_top-join_depth)*extrude(f,relief_height+join_depth) for f in polygon_glyph_faces("Makit",logo_size,curve_tolerance)])
# Keep the actual solid in B-rep form: no triangular faces across the visible flat artwork.
s=s.fuse(grid_relief,*raised).clean()
print("native_dial_faces",len(s.faces()),"glyph_outline_tolerance_mm",curve_tolerance)

# Projected movement outline on the inside face; this is an engraving, not a locating wall.
movement_length=param("dial_movement_length",56.0)
movement_width=param("dial_movement_width",56.0)
movement_corner_r=param("dial_movement_corner_radius",3.0)
movement_line_w=param("dial_movement_line_width",0.5)
movement_line_depth=param("dial_movement_line_depth",0.2)
movement_x=param("dial_movement_offset_x",0.0)
movement_y=param("dial_movement_offset_y",0.0)
movement_outline=RectangleRounded(movement_length+movement_line_w,movement_width+movement_line_w,movement_corner_r+movement_line_w/2)-RectangleRounded(movement_length-movement_line_w,movement_width-movement_line_w,movement_corner_r-movement_line_w/2)
movement_etch=Pos(movement_x,movement_y,dial_back_z-0.01)*extrude(movement_outline,movement_line_depth+0.01)
# Concentric groove at the centre of the blank annular band.
# Width/depth are derived from the user's existing grid, not independent duplicates.
rim_groove_radius=(art_radius+dial_radius)/2
rim_groove_width=line_width
rim_groove_depth=grid_height
assert lip_start<rim_groove_radius-rim_groove_width/2<rim_groove_radius+rim_groove_width/2<dial_radius-1
rim_tool_bottom=flat_top-rim_groove_depth-0.01
rim_annulus=Pos(0,0,rim_tool_bottom)*extrude(Circle(rim_groove_radius+rim_groove_width/2)-Circle(rim_groove_radius-rim_groove_width/2),lip_top-rim_tool_bottom+0.01)
# Subtract the lowered blank to make the cutter follow the original analytic arc.
rim_groove_tool=rim_annulus.cut(Pos(0,0,-rim_groove_depth)*dial_blank)
s=s.cut(movement_etch,rim_groove_tool)
print("rim_groove_radius_width_depth",rim_groove_radius,rim_groove_width,rim_groove_depth)
print("movement_projected_outline",movement_length,movement_width,movement_corner_r,"etch",movement_line_w,movement_line_depth)

assert s.is_valid and len(s.solids())==1, "Relief and dial must be one watertight solid"
assert len(led_centers)==10 and all((-x,y) in led_centers for x,y in led_centers)
print("One integral dial; grid width/height",line_width,grid_height,"markings",relief_height,"cardinal",cardinal_width,cardinal_length)
s.color=srgb("#F5F3EC")
publish("dial",s,"一体浮雕网格表盘",material="petg")