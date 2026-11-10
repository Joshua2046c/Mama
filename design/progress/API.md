# 本地进度灯接口（固件源码草案）

硬件目标：Seeed Studio XIAO ESP32C3，D10/GPIO10经AHCT缓冲和330Ω驱动十颗WS2812B-2020-V6。电脑应用由用户编写；本文件定义设备端接口。源码尚未编译或烧录，不能把接口草案当作已验证的实机能力。

首次启动：连接设备热点`Makit-Clock-<设备后缀>`，默认热点密码`makitclock`，浏览器访问`http://192.168.4.1/`。读取并保存设备令牌，填写2.4GHz Wi-Fi名称、密码及设备名称。设备重启后进入该局域网；后续通过`http://<设备名称>.local/`或设备IP访问配置页。网络暂时失败30秒后启用恢复热点；运行中长按BOOT超过4秒清除网络配置，保留设备令牌。热点是首次配网和恢复通道，日常配置、查询和进度更新在同一局域网内完成。

LED索引：正面观看，上行从左到右0–4（Y45.5mm），下行从左到右5–9（Y31.5mm）。每行X为−28/−14/0/14/28mm。所有更新以十灯完整快照一次替换，不把上行/下行语义锁死在硬件中。默认空闲灭、等待白、运行黄、完成绿、错误红；电脑可发送任意RGB颜色。30秒未收到更新时保留末次状态并低亮脉冲；没有历史状态则保持灭灯。重启不恢复旧进度，等待电脑发送新快照，避免断电后误显示完成。

## HTTP

- `GET /`：本地配置页。
- `GET /api/v1/setup`：仅设备热点接口可读取首次配置令牌。
- `GET /api/v1/status`：设备名称、入网状态、IP、10灯颜色、亮度、是否超时及最后sequence；不返回Wi-Fi密码或令牌。
- `PUT /api/v1/pixels`：需要`X-Clock-Token`请求头；JSON包含`colors`或`states`，二者恰好一个，数组长度必须10。可选`brightness`范围0–0.25，可选`sequence`为32位非负整数，只回显，不承担跨会话排序。每次有效请求刷新30秒状态期限。
- `POST /api/v1/config`：JSON字符串`ssid`、`password`、`device_name`，需要令牌；首次设备热点允许直接配置。202表示已保存，约1.2秒后重启。设备名为1–24位小写字母、数字、非首尾连字符。Wi-Fi密码允许空串（开放网络）或8–63位；本项目默认用于受信任局域网，无云端服务。

请求示例（将主机名和令牌替换成实机值）：

```sh
curl -X PUT 'http://makit-clock.local/api/v1/pixels' \
  -H 'Content-Type: application/json' \
  -H 'X-Clock-Token: YOUR_DEVICE_TOKEN' \
  --data '{"states":["running","running","running","running","running","complete","complete","complete","complete","complete"],"brightness":0.15,"sequence":42}'
```

```json
{"colors":["#FFFFFF","#FFFFFF","#FFFFFF","#FFFFFF","#FFFFFF","#FFFFFF","#FFFFFF","#FFFFFF","#FFFFFF","#00FF00"],"brightness":0.10,"sequence":43}
```

成功返回`{"ok":true,"sequence":42}`。400为参数错误，401为令牌不匹配，413为请求超过4096字节。电脑端建议每5–10秒发送全量快照并在重新连接时立刻刷新。无需把用户电脑软件写进时钟。

## 构建与实机验证

固件提供PlatformIO配置，固定espressif32 6.10.0（Arduino2.0.17）及ArduinoJson7.4.2；RMT驱动直接产生V6数据时序：0为0.30/0.95µs，1为0.60/0.65µs，GRB高位先发，复位400µs。引脚来自Seeed官方定义。参考：https://docs.platformio.org/en/latest/boards/espressif32/seeed_xiao_esp32c3.html 、https://docs.espressif.com/projects/esp-idf/en/v4.4.7/esp32c3/api-reference/peripherals/rmt.html 。

本机未找到PlatformIO或Arduino CLI，未编译；未做Wi-Fi、脉冲、断网重连和整机亮度实测。原理图/布局预览可编译；制造检查仍被封装坐标转换错误阻断，尚无Gerber、钻孔和已验证PCB STEP。先恢复板级制造检查，再编译固件、烧录并用逻辑分析仪核对时序，最后验证10灯RGB、USB正反插、配网和断网恢复。连接XIAO自身USB编程前拔掉内部供电线，避免两路USB同时送电。
