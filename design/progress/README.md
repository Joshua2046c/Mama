# RGB progress carrier
80×172 mm two-layer carrier, board centered on clock axis; central 60×58 mm chamfered opening clears the 56×56 mm movement. Board rear target Z=22.8 mm (envelope precheck only), LED face +Z. Ten LEDs on front, XIAO/logic/power connector on back above the LED array, to keep the dial flat. XIAO ESP32C3 vendor footprint and D10=GPIO10 from official Seeed pinout. External supplied antenna must stay inside uncoated plastic sector, away from AA battery and copper. Silver finish must be nonconductive.

WS2812B-2020-V6 datasheet visually inspected pp2–6: DO1/GND2/DI3/VDD4, 0.84 mm height, 12 mA/channel, VIH 0.55 VDD, GRB MSB first, reset >280 us. Use 400 us reset. V6 is not interchangeable with older 2020 footprints. Local 100nF capacitors and 10uF input bulk stabilize wiring. AHCT1G125 datasheet pp3–4,9–11: 4.5–5.5V rail, 2V VIH, OE tied GND, input held low by100k, 100nF by supply pin; 330 ohm output damping. SS14 feeds XIAO 5V pin per vendor advice, never put LED load on XIAO3V3.

Prototype assembly: stencil/reflow or skilled manual assembly of listed exact parts, XIAO soldered castellations. No supplier assembly placement verification claimed. Inter-board harness pin1 +5V/red, pin2 GND/black. Unplug main power harness before connecting XIAO service USB. Four 2.5 mm NPTH are intended to locate on 2.0 mm adhesive-supported pins; retainers are not yet modeled. No screws are specified. Final placement and power routing remain subject to compile/DRC/release and CAD fit checks.

## Validation boundary
Independent final KiCad DRC: 0 errors, 18 bottom-side library footprint mismatch warnings, 0 unconnected items. All signal/power nets and filled GND are connected; the router pre-fill summary alone is not final connectivity. Added a1.1mm conservative routing keepout around the unchanged movement cutout while retaining1mm board-edge copper clearance. All ten LED positions stay fixed. The control/power parts now occupy the upper backside; use a160mm internal harness. C11 relocation eliminated the final GND island; moving only the XIAO Reference text eliminated silk overlaps.

The formal check is blocked solely at routed-copper calibration: center-based fitting reproduces1.224642857mm residual, whereas footprint-origin fitting of all28 components gives approximately0mm. The corresponding small-board residual is0.931000180mm, also0mm with origins. See the read-only reproducer and evidence in review/. No manufacturing Release, verified assembly STEP or final board-retention model exists. Firmware is uncompiled and untested. Envelope checks are preliminary and do not establish installed assembly fit.

## 2026-11-10 采购前复核
两板正式check仍在坐标回写阶段阻塞，残差为主板1.224642857mm、小板0.931000180mm；按footprint_origin只读拟合均约0mm。没有发布制造包。
本次独立KiCad DRC：0错误、18条底面库封装一致性警告、0未连接。返回的正反面和原理图已查看；因回写失败，正式路由观察仍拒绝当前文件的一致性，因此视觉审核记为partial。供应商料号、LED/缓冲器/USB-C针脚已复核；详细记录见review。不得将当前预览或临时KiCad文件用于下单。
当前壳内已按四个Ø2.5定位孔预留Ø2.1定位销与0.1mm胶层；小板已有边缘卡槽。实际装配仍待释放STEP验证。
