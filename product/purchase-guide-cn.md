# 中国大陆采购清单与电路板审核

核查日期：2026-11-10。装机数量按一台计算，购买数量受商家最小包装限制。零件清单已补入国内渠道；本文件不是PCB投板许可。

## 电路板审核结论

| 板 | 独立KiCad DRC几何错误 | 警告 | 未连接 | 正式制造检查 |
|---|---:|---:|---:|---|
| RGB主板 | 0 | 18条底面库封装一致性 | 0 | 坐标回写残差1.224642857mm，阻塞 |
| USB-C小板 | 0 | 0 | 1处地铜区域 | 坐标回写残差0.931000180mm，阻塞 |

两板均不能下单。使用封装原点作只读拟合时残差约0，使用几何中心则精确复现错误；没有修改生成文件或绕开检查。供电小板的未连接报告只给出整个铜区的锚点，不能当作补过孔的位置。局部铜区诊断与坐标回写均需解决后重新运行正式检查。

十灯LED链、D10/GPIO10、电平缓冲器针脚、独立CC下拉与5V路径已对照当前源码及供应商资料复核。两板当前的正反面预览和原理图已查看，但路由观察因回写失败认定输出不一致，所以视觉审核为partial。真实元件装壳、天线性能、实物供电及固件功能未验证。

## 建议购买方式

若交给贴片厂包料，下面的板上器件清单交给工厂即可，不要重复买散件。现有原型按人工贴片/半孔焊接，未提供可直接下单的SMT生产包。XIAO买未焊排针版本，保留原配天线；USB-C只输入5V，机芯继续用自带电池，不买锂电池、充电板或升压板。

精确商品链接有供应商料号；“规格搜索”仅提供筛选入口，不代表搜索结果均兼容。价格和库存以下单页为准。

## 板上器件

| 部件 | 确切型号 / 料号 | 每台用量 | 国内链接 | 采购提示 |
|---|---|---:|---|---|
| wifi_controller | 113991054  | 1 | [购买](https://spotpear.cn/shop/Seeed-Studio-XIAO-ESP32C3-Tiny-SuperMini/XIAO-ESP32C3.html) | 买未焊排针版本，用半孔焊到主板；使用原配2.4GHz天线，不买SuperMini替代板。 |
| rgb_led | WS2812B-2020-V6 C52917434 | 10 | [购买](https://item.szlcsc.com/55827425.html) | 供应商起订5只；数量为每台装机用量；贴片代工包料时不要重复购买。 |
| level_buffer | SN74AHCT1G125DBVR C7484 | 1 | [购买](https://item.szlcsc.com/7961.html) | 供应商起订5只；数量为每台装机用量；贴片代工包料时不要重复购买。 |
| usb_c | TYPE-C-31-M-12 C165948 | 1 | [购买](https://item.szlcsc.com/177331.html) | 供应商起订5只；数量为每台装机用量；贴片代工包料时不要重复购买。 |
| xiao_power_isolation | SS14 C2480 | 1 | [购买](https://item.szlcsc.com/2857.html) | 供应商起订50只；数量为每台装机用量；贴片代工包料时不要重复购买。 |
| decoupling | CC0603KRX7R9BB104 C14663 | 11 | [购买](https://item.szlcsc.com/15331.html) | 原C14663本次无现货；[C1591 / CL10B104KB8NNNC](https://item.szlcsc.com/1943.html)为100nF/50V/X7R/0603候选，未替换原设计。 |
| bulk | CL21A106KAYNNNE C15850 | 2 | [购买](https://item.szlcsc.com/16532.html) | 供应商起订20只；数量为每台装机用量；贴片代工包料时不要重复购买。 |
| usb_rd | 0603WAF5101T5E C23186 | 2 | [购买](https://item.szlcsc.com/23913.html) | 供应商起订100只；数量为每台装机用量；贴片代工包料时不要重复购买。 |
| data_series | 0603WAF3300T5E C23138 | 1 | [购买](https://item.szlcsc.com/23865.html) | 供应商起订100只；数量为每台装机用量；贴片代工包料时不要重复购买。 |
| data_pulldown | 0603WAF1003T5E C25803 | 1 | [购买](https://item.szlcsc.com/26546.html) | 供应商起订100只；数量为每台装机用量；贴片代工包料时不要重复购买。 |
| power_headers | HX PZ2.54-1x2P ZZ C32713268 | 2 | [购买](https://item.szlcsc.com/34444548.html) | 供应商起订5只；1×2P、2.54mm、0.64mm方针、塑高2.5mm、配接端6mm、焊脚3mm；保留现有KiCad标准封装及BOM绑定身份。 |

## 机电、线材与装配耗材

| 部件 | 每台数量 | 国内链接 | 必须匹配的规格 |
|---|---:|---|---|
| UGREEN 绿联 CD146 双USB-A可折叠充电器，选5V/2.4A口配USB-A转USB-C线；满足原5V≥1A供电要求 | 1 | [商品](https://detail.tmall.com/item.htm?id=39662398527) | 已有合格5V≥1A适配器可复用；新购使用2.4A口，店铺页面可能需要登录。 |
| USB-A转USB-C细头供电/数据线，约1m；C头注塑外壳≤12×8×20mm，线径≤4mm | 1 | [规格搜索](https://s.taobao.com/search?q=USB%20A%20%E8%BD%AC%20Type%20C%20%E7%BB%86%E5%A4%B4%20%E6%95%B0%E6%8D%AE%E7%BA%BF%201%E7%B1%B3) | 搜索入口不是已核定的具体商品；按C头注塑外壳尺寸筛选，先试穿底座，编织加粗/大直角头不默认适配。数据线可兼作XIAO烧录。 |
| 26 AWG two-conductor red/black insulated internal power harness, 160 mm, 2.54 mm 2-pin housings at both ends | 1 | [规格搜索](https://s.taobao.com/search?q=26AWG%20%E6%9D%9C%E9%82%A6%E7%BA%BF%202P%20%E6%AF%8D%E5%AF%B9%E6%AF%8D%202.54%2016cm%20%E7%BA%A2%E9%BB%91) | 红黑两芯，2.54mm 2P母对母，160mm，26AWG；1脚红+5V，2脚黑GND。常见细28/30AWG线不作为本项指定型号。 |
| User-selected adhesive suitable for PETG rail bonds and all magnet pockets; check magnet polarity before bonding | 1 | [规格搜索](https://s.taobao.com/search?q=PETG%20%E9%92%95%E9%93%81%E7%A1%BC%20%E7%A3%81%E9%93%81%20%E5%8F%8C%E7%BB%84%E5%88%86%20%E7%8E%AF%E6%B0%A7%20AB%E8%83%B6) | 双组分环氧胶/原指定胶，先做PETG与磁铁小样，确认极性后胶合；一组供滑轨与磁铁使用。 |
| Nonconductive0.1mm mounting adhesive pads for four PCB support lands,4.4mm outer diameter with2.6mm pin clearance | 4 | [规格搜索](https://s.taobao.com/search?q=0.1mm%20PET%20%E7%BB%9D%E7%BC%98%20%E5%8F%8C%E9%9D%A2%E8%83%B6) | 非导电0.1mm厚胶，需4个外径4.4mm、中孔2.6mm小垫圈；裁切时保留定位销让位。 |
| Black opaque 0.25 mm foam or gasket tape to seal diffuser flanges to baffle; keep LED windows clear | 1 | [规格搜索](https://s.taobao.com/search?q=0.25mm%20%E9%BB%91%E8%89%B2%20%E9%81%AE%E5%85%89%20%E6%B3%A1%E6%A3%89%20%E8%83%B6%E5%B8%A6) | 黑色不透光、厚0.25mm；可买一卷裁条封光，不能覆盖灯窗。 |
| White base finish, blue numeral/tick finish, red grid/quadrant-marker finish and silver shell finish suitable for PETG | 1 | [规格搜索](https://s.taobao.com/search?q=%E6%B0%B4%E6%80%A7%E6%A8%A1%E5%9E%8B%E6%BC%86%20PETG%20%E7%99%BD%E8%89%B2%20%E8%93%9D%E8%89%B2%20%E7%BA%A2%E8%89%B2%20%E9%93%B6%E8%89%B2) | 白/蓝/红/银非导电表面涂料一套；天线区保持未金属化塑料，先检验附着。 |
| Generic AA quartz movement, 14 mm shaft, 56 x 56 x 17 mm class | 1 | [规格搜索](https://s.taobao.com/search?q=%E7%9F%B3%E8%8B%B1%20%E6%89%AB%E7%A7%92%20%E6%9C%BA%E8%8A%AF%2056%2056%2017%2014mm%20%E8%BD%B4) | 沿用用户指定56mm机芯。此链接仅为规格检索，没有核到完全相同机型；未买时先核壳体、14mm轴总长/螺纹长度、指针接口，不直接替代。 |
| 9084 style clock hand set, user maximum radius 90 mm; supplied picture also labels minute hand 102 mm | 1 | [规格搜索](https://s.taobao.com/search?q=9084%20%E7%9F%B3%E8%8B%B1%E9%92%9F%20%E6%8C%87%E9%92%88) | 沿用用户指定9084样式；接口须与原机芯成套匹配，搜索链接不能证明兼容。 |
| 1.5 V AA battery | 1 | [规格搜索](https://s.taobao.com/search?q=5%E5%8F%B7%20AA%201.5V%20%E7%A2%B1%E6%80%A7%20%E7%94%B5%E6%B1%A0) | 机芯自带电池槽；已有电池可复用，本次不新增锂电池或充电模块。 |
| 圆片磁铁 | 合计10颗，建议12颗含备件 | [7×1mm商品](https://www.yiwugo.com/product/detail/928444734.html) | 表盘8颗+后盖2颗；直径7×厚1mm。标题匹配，动态页面库存与公差未核。 |

机芯与指针沿用用户已指定款。尚未核到完全相同的56×56×17mm、14mm总轴长机芯的国内商品，搜索入口不可作为替代型号确认；有原机芯时无需重复采购。

## 定制件：暂不要下单的电路板与打印件

- RGB主板：80×172mm、FR4双层、1.6mm、1oz、中央60×58mm机芯避让孔，1块；等待正式检查和制造发布。
- USB-C供电小板：22×16mm、FR4双层、1.6mm、1oz，1块；等待地铜连接与正式检查。
- 打印件共17件：钟壳、表盘、底座、后盖、左右滑轨各1件，乳白半透PETG扩散窗10件，黑色PETG遮光件1件。主体和扩散窗材料需分开选择；打印件按模型制作，没有现货采购型号。
- 固定不需要另买螺丝/铜柱；当前采用壳内一体定位柱、卡槽和绝缘胶垫。

## 上电与程序准备

组装后先核红线+5V、黑线GND，再测试5V电源和LED；XIAO服务USB与外部供电不要同时接入，先拔内部电源线束。XIAO程序尚未编译和烧录；电脑端软件也需对接现有LAN接口。烧录按[Seeed官方入门指南](https://wiki.seeedstudio.com/XIAO_ESP32C3_Getting_Started/)：使用可传数据的USB-C线连接电脑，Arduino IDE安装Espressif ESP32板支持，选择XIAO ESP32C3板和串口后上传设备端程序。供电小板的Type-C口仅供电，烧录应接XIAO自身USB口。

现成主控也可从[Seeed国内官方渠道](https://www.seeedstudio.com.cn/purchase)购买相同113991054未焊排针版。
