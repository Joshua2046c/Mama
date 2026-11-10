export const board={width:"22mm",height:"16mm"};
export const OPENING_ROTATION_DEG={up:0,left:90,down:180,right:270} as const;
export function rotationForOpening(a:keyof typeof OPENING_ROTATION_DEG,b:keyof typeof OPENING_ROTATION_DEG){return (OPENING_ROTATION_DEG[b]-OPENING_ROTATION_DEG[a]+360)%360;}
export const usb={x:0,y:-3.3,targetOpening:"down" as const};
