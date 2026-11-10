import {board,usb,rotationForOpening} from "./layout";
import {boardPropsFromRules,groundPourPropsFromRules,keepoutPropsFromRules,netPropsFor,pcbRules} from "./lib/makit-pcb";
export default ()=> <board width={board.width} height={board.height} center_x={0} center_y={0} {...boardPropsFromRules()}>
{Object.keys(pcbRules.nets).map(n=><net key={n} name={n} {...netPropsFor(n)}/>)}{groundPourPropsFromRules().map(p=><copperpour key={p.name} {...p}/>)}{keepoutPropsFromRules().map(p=><keepout {...p}/>)}
<connector name="J_USB" allowOffBoard standard="usb_c" footprint="jlcpcb:C165948" supplierPartNumbers={{jlcpcb:["C165948"]}} manufacturerPartNumber="TYPE-C-31-M-12" pcbX={usb.x} pcbY={usb.y} pcbRotation={rotationForOpening("down",usb.targetOpening)} layer="top" schSectionName="5V USB-C input" connections={{VBUS1:"net.V5",VBUS2:"net.V5",GND1:"net.GND",GND2:"net.GND",CC1:"net.CC1",CC2:"net.CC2",EH1:"net.GND",EH2:"net.GND",EH3:"net.GND",EH4:"net.GND"}}/>
<resistor name="R_CC1" resistance="5.1k" footprint="jlcpcb:C23186" supplierPartNumbers={{jlcpcb:["C23186"]}} pcbX={-5} pcbY={2} schSectionName="5V USB-C input" connections={{pin1:"net.CC1",pin2:"net.GND"}}/>
<resistor name="R_CC2" resistance="5.1k" footprint="jlcpcb:C23186" supplierPartNumbers={{jlcpcb:["C23186"]}} pcbX={3.5} pcbY={2} schSectionName="5V USB-C input" connections={{pin1:"net.CC2",pin2:"net.GND"}}/>
<capacitor name="C13" capacitance="10uF" footprint="jlcpcb:C15850" supplierPartNumbers={{jlcpcb:["C15850"]}} pcbX={-5} pcbY={5} schSectionName="5V USB-C input" connections={{pin1:"net.V5",pin2:"net.GND"}}/>
<chip name="J_OUT" pcbPositionAnchor="center" footprint="kicad:Connector_PinHeader_2.54mm/PinHeader_1x02_P2.54mm_Vertical" pcbX={7.5} pcbY={4} layer="top" pinLabels={{pin1:"V5",pin2:"GND"}} schSectionName="5V USB-C input" connections={{V5:"net.V5",GND:"net.GND"}}/>
</board>;
