# Hidden USB-C power entry
22×16 mm perpendicular PCB in lower rear clock cavity, connector mating from base storage interior through rear opening. Connector TYPE-C-31-M-12 C165948 drawing p1: 8.94mm shell width, 3.26mm max total height, four plated shield slots and two 0.6mm NPTH locators. Two separate5.1k CC pulldowns for either cable orientation, no PD request, no USB data. Regulated5V >=1A supply required. Only connects when clock seated; unplug before sliding clock upward. Main harness and board retention are internal. Final position must be based on released geometry.

## Validation boundary
Independent final KiCad DRC: 0 errors, 0 warnings, 0 unconnected items. Source nominal V5 width0.5mm now fits the supplier0.6mm VBUS land; source manufacturing limits remain unchanged. Both VBUS lands, both CC pull-downs and the output harness are connected. No compensating copper-area geometry remains.

The formal check is still blocked by0.931000180mm center-based coordinate calibration error. A read-only comparison of all5 footprint origins gives exactly0mm residual at the common board transform. This is not a published Build or Release: no manufacturing package or release-bound assembly STEP exists. USB-C real body, four shield slots, mounting, cable insertion/removal and solder clearance must be checked in that STEP before final installation approval. See progress/review/coordinate-conversion.md for reproduction.

## 2026-11-10 采购前复核
两板正式check仍在坐标回写阶段阻塞，残差为主板1.224642857mm、小板0.931000180mm；按footprint_origin只读拟合均约0mm。没有发布制造包。
本次独立KiCad DRC：0几何违规，但1处GND铜区未连接；旧版0未连接结论只适用于历史输出。返回的正反面和原理图已查看；因回写失败，正式路由观察仍拒绝当前文件的一致性，因此视觉审核记为partial。供应商料号、LED/缓冲器/USB-C针脚已复核；详细记录见review。不得将当前预览或临时KiCad文件用于下单。
