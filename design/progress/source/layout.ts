export const board = { width: "80mm", height: "172mm", centerY: 0 };
// Board coordinates equal clock front coordinates; quartz clearance is 60 x 58.
// Exact LED locations are shared with CAD and optical drawing.
export const leds = [31.5,45.5].flatMap((y,row)=>[-28,-14,0,14,28].map((x,col)=>({x,y,index:(1-row)*5+col,ref:`D${(1-row)*5+col+1}`}))).sort((a,b)=>a.index-b.index);
export const OPENING_ROTATION_DEG = {up:0,left:90,down:180,right:270} as const;
export type OpeningDirection = keyof typeof OPENING_ROTATION_DEG;
export function rotationForOpening(a:OpeningDirection,b:OpeningDirection){return (OPENING_ROTATION_DEG[b]-OPENING_ROTATION_DEG[a]+360)%360;}
