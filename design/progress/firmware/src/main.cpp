#include <Arduino.h>
#include <WiFi.h>
#include <WebServer.h>
#include <ESPmDNS.h>
#include <Preferences.h>
#include <driver/rmt.h>
#include <esp_err.h>
#include <ArduinoJson.h>
#include <math.h>

// Official Seeed pins_arduino.h: D10 = GPIO10, BOOT = GPIO9.
constexpr uint8_t PIXEL_PIN = 10, BOOT_PIN = 9, COUNT = 10;
constexpr float MAX_BRIGHTNESS = 0.25f;
constexpr uint32_t STALE_MS = 30000;
uint32_t displayed[COUNT] = {};
rmt_item32_t frame[COUNT * 24 + 1];
void showPixels() {
  int k=0;
  for(int p=0;p<COUNT;p++) {
    uint32_t c=displayed[p];
    uint8_t grb[3]={(uint8_t)(c>>8),(uint8_t)(c>>16),(uint8_t)c};
    for(auto byte:grb)for(int b=7;b>=0;b--) {
      bool one=byte & (1<<b);frame[k].level0=1;frame[k].duration0=one?24:12;
      frame[k].level1=0;frame[k].duration1=one?26:38;k++;
    }
  }
  // 40MHz RMT clock: 0-bit .30/.95us; 1-bit .60/.65us; reset400us.
  frame[k].level0=0;frame[k].duration0=16000;frame[k].level1=0;frame[k].duration1=1;
  ESP_ERROR_CHECK(rmt_write_items(RMT_CHANNEL_0,frame,k+1,true));
}
WebServer server(80);
Preferences prefs;
String ssid, password, hostName, token;
uint32_t colors[COUNT] = {}, lastUpdate = 0, lastReconnect = 0, buttonSince = 0;
uint32_t restartAt = 0, sequence = 0, wifiLostAt = 0, lastFrame = 0;
float brightness = 0.15f;
bool apRunning = false, mdnsRunning = false, haveUpdate = false, buttonHeld = false;

const char PAGE[] PROGMEM = R"HTML(<!doctype html><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>Makit Clock</title>
<style>body{font:17px system-ui;max-width:34em;margin:3em auto;padding:1em;background:#f5f3ec;color:#153763}label{display:block;margin:1em 0}input,button{font:inherit;padding:.5em;width:95%}button{background:#153763;color:white;border:0}pre{white-space:pre-wrap;word-break:break-all}</style>
<h1>Makit Clock</h1><p>本地网络配置。首次连接设备热点后先读取设备令牌；已入网设备请填写保存的令牌。</p>
<label>设备令牌<input id="token" autocomplete="off"></label><button onclick="setup()">读取首次配置令牌</button>
<label>Wi-Fi 名称<input id="ssid" maxlength="32"></label><label>Wi-Fi 密码<input id="password" type="password" maxlength="63"></label>
<label>设备名称<input id="name" value="makit-clock" maxlength="24"></label><button onclick="save()">保存并连接局域网</button><pre id="out"></pre>
<script>async function setup(){let r=await fetch('/api/v1/setup');let j=await r.json();if(r.ok)document.getElementById('token').value=j.token;document.getElementById('out').textContent=JSON.stringify(j,null,2)}
async function save(){let r=await fetch('/api/v1/config',{method:'POST',headers:{'Content-Type':'application/json','X-Clock-Token':document.getElementById('token').value},body:JSON.stringify({ssid:document.getElementById('ssid').value,password:document.getElementById('password').value,device_name:document.getElementById('name').value})});document.getElementById('out').textContent=await r.text()}</script>)HTML";

void jsonReply(int status, JsonDocument &doc) { String s; serializeJson(doc,s); server.send(status,"application/json",s); }
void fail(int status,const char *message) { JsonDocument j;j["error"]=message;jsonReply(status,j); }
bool viaAP() { return apRunning && server.client().localIP()==WiFi.softAPIP(); }
bool authorized() { if(server.header("X-Clock-Token")==token)return true;fail(401,"X-Clock-Token required");return false; }
bool readJson(JsonDocument &j) {
  String body=server.arg("plain");if(body.length()>4096){fail(413,"request exceeds 4096 bytes");return false;}
  if(deserializeJson(j,body)){fail(400,"invalid JSON");return false;}
  if(!j.is<JsonObject>()){fail(400,"JSON object required");return false;}return true;
}
bool parseColor(const char *s,uint32_t &out) {
  if(!s || strlen(s)!=7 || s[0]!='#')return false;
  uint32_t v=0;for(int i=1;i<7;i++){char c=s[i];int d=c>='0'&&c<='9'?c-'0':c>='a'&&c<='f'?c-'a'+10:c>='A'&&c<='F'?c-'A'+10:-1;if(d<0)return false;v=(v<<4)|d;}out=v;return true;
}
bool stateColor(const char *s,uint32_t &out) {
  if(!s)return false;
  if(!strcmp(s,"idle"))out=0;
  else if(!strcmp(s,"queued"))out=0xffffff;
  else if(!strcmp(s,"running"))out=0xffb000;
  else if(!strcmp(s,"complete"))out=0x00ff20;
  else if(!strcmp(s,"error"))out=0xff1000;
  else return false;return true;
}
void beginAP(){if(apRunning)return;WiFi.mode(WIFI_AP_STA);String ap="Makit-Clock-"+String((uint32_t)ESP.getEfuseMac(),HEX);apRunning=WiFi.softAP(ap.c_str(),"makitclock");Serial.printf("Setup SSID %s password makitclock at 192.168.4.1\n",ap.c_str());}
void setup(){
  Serial.begin(115200);pinMode(BOOT_PIN,INPUT_PULLUP);rmt_config_t rc={};rc.rmt_mode=RMT_MODE_TX;rc.channel=RMT_CHANNEL_0;rc.gpio_num=(gpio_num_t)PIXEL_PIN;rc.clk_div=2;rc.mem_block_num=1;
  rc.tx_config.loop_en=false;rc.tx_config.carrier_en=false;rc.tx_config.idle_output_en=true;rc.tx_config.idle_level=RMT_IDLE_LEVEL_LOW;
  ESP_ERROR_CHECK(rmt_config(&rc));ESP_ERROR_CHECK(rmt_driver_install(RMT_CHANNEL_0,0,0));showPixels();
  prefs.begin("makit-clock",false);ssid=prefs.getString("ssid","");password=prefs.getString("pass","");hostName=prefs.getString("name","makit-clock");token=prefs.getString("token","");
  if(token.length()!=32){char b[33];snprintf(b,sizeof b,"%08lx%08lx%08lx%08lx",(unsigned long)esp_random(),(unsigned long)esp_random(),(unsigned long)esp_random(),(unsigned long)esp_random());token=b;prefs.putString("token",token);}
  Serial.printf("Local API token: %s\n",token.c_str());
  WiFi.mode(WIFI_STA);WiFi.setHostname(hostName.c_str());WiFi.setAutoReconnect(true);if(ssid.length())WiFi.begin(ssid.c_str(),password.c_str());else beginAP();
  const char *headers[]={"X-Clock-Token"};server.collectHeaders(headers,1);
  server.on("/",HTTP_GET,[]{server.send_P(200,"text/html; charset=utf-8",PAGE);});
  server.on("/api/v1/setup",HTTP_GET,[]{if(!viaAP()){fail(403,"setup token is available only through device setup AP");return;}JsonDocument j;j["token"]=token;j["device_name"]=hostName;jsonReply(200,j);});
  server.on("/api/v1/status",HTTP_GET,[]{
    JsonDocument j;j["device_name"]=hostName;j["connected"]=WiFi.status()==WL_CONNECTED;j["ip"]=WiFi.localIP().toString();j["pixels"]=COUNT;j["brightness"]=brightness;j["max_brightness"]=MAX_BRIGHTNESS;j["sequence"]=sequence;j["stale"]=!haveUpdate || uint32_t(millis()-lastUpdate)>STALE_MS;
    JsonArray a=j["colors"].to<JsonArray>();for(auto c:colors){char b[8];snprintf(b,sizeof b,"#%06lx",(unsigned long)c);a.add(b);}jsonReply(200,j);
  });
  server.on("/api/v1/pixels",HTTP_PUT,[]{
    if(!authorized())return;JsonDocument j;if(!readJson(j))return;uint32_t next[COUNT];float nextBrightness=brightness;
    bool hasColors=j["colors"].is<JsonArray>(),hasStates=j["states"].is<JsonArray>();
    if(hasColors==hasStates){fail(400,"supply exactly one of colors[10] or states[10]");return;}
    JsonArray a=hasColors?j["colors"].as<JsonArray>():j["states"].as<JsonArray>();if(a.size()!=COUNT){fail(400,"exactly 10 pixel values required");return;}
    for(int i=0;i<COUNT;i++){bool ok=hasColors?parseColor(a[i].as<const char*>(),next[i]):stateColor(a[i].as<const char*>(),next[i]);if(!ok){fail(400,"invalid pixel color or state");return;}}
    if(!j["brightness"].isNull()){if(!j["brightness"].is<float>()&&!j["brightness"].is<int>()){fail(400,"brightness must be numeric");return;}nextBrightness=j["brightness"].as<float>();if(!isfinite(nextBrightness)||nextBrightness<0||nextBrightness>MAX_BRIGHTNESS){fail(400,"brightness must be between 0 and 0.25");return;}}
    if(!j["sequence"].isNull()&&!j["sequence"].is<uint32_t>()){fail(400,"sequence must be unsigned integer");return;}
    for(int i=0;i<COUNT;i++)colors[i]=next[i];brightness=nextBrightness;sequence=j["sequence"]|uint32_t(0);lastUpdate=millis();haveUpdate=true;
    JsonDocument reply;reply["ok"]=true;reply["sequence"]=sequence;jsonReply(200,reply);
  });
  server.on("/api/v1/config",HTTP_POST,[]{
    if(!viaAP()&&!authorized())return;JsonDocument j;if(!readJson(j))return;
    if(!j["ssid"].is<const char*>()||!j["password"].is<const char*>()||!j["device_name"].is<const char*>()){fail(400,"ssid, password and device_name strings required");return;}
    String s=j["ssid"].as<String>(),p=j["password"].as<String>(),h=j["device_name"].as<String>();
    if(s.length()<1||s.length()>32||p.length()>63||(p.length()>0&&p.length()<8)||h.length()<1||h.length()>24){fail(400,"invalid SSID/password/name length");return;}
    for(unsigned i=0;i<h.length();i++)if(!(h[i]>='a'&&h[i]<='z')&&!(h[i]>='0'&&h[i]<='9')&&h[i]!='-'){fail(400,"device_name uses lowercase a-z, 0-9 and hyphen");return;}
    if(h[0]=='-'||h[h.length()-1]=='-'){fail(400,"name cannot begin/end with hyphen");return;}
    prefs.putString("ssid",s);prefs.putString("pass",p);prefs.putString("name",h);JsonDocument reply;reply["ok"]=true;reply["restart"]=true;reply["device_name"]=h;jsonReply(202,reply);restartAt=millis()+1200;
  });
  server.onNotFound([]{fail(404,"not found");});server.begin();wifiLostAt=millis();
}
void loop(){
  server.handleClient();uint32_t now=millis();
  if(restartAt && int32_t(now-restartAt)>=0)ESP.restart();
  if(digitalRead(BOOT_PIN)==LOW){if(!buttonHeld){buttonSince=now;buttonHeld=true;}else if(uint32_t(now-buttonSince)>4000){prefs.remove("ssid");prefs.remove("pass");ESP.restart();}}else buttonHeld=false;
  bool connected=WiFi.status()==WL_CONNECTED;
  if(connected){wifiLostAt=now;if(!mdnsRunning){mdnsRunning=MDNS.begin(hostName.c_str());if(mdnsRunning){MDNS.addService("http","tcp",80);MDNS.addServiceTxt("http","tcp","product","makit-progress-clock");}}}
  else {if(mdnsRunning){MDNS.end();mdnsRunning=false;}if(uint32_t(now-wifiLostAt)>30000)beginAP();if(ssid.length()&&uint32_t(now-lastReconnect)>10000){lastReconnect=now;WiFi.reconnect();}}
  if(uint32_t(now-lastFrame)>=40){lastFrame=now;bool stale=!connected||!haveUpdate||uint32_t(now-lastUpdate)>STALE_MS;float scale=brightness;
    if(stale)scale*=0.20f+0.15f*(0.5f+0.5f*sinf(now*0.00314159265f));
    for(int i=0;i<COUNT;i++){uint32_t c=colors[i];uint8_t r=((c>>16)&255)*scale,g=((c>>8)&255)*scale,b=(c&255)*scale;displayed[i]=(uint32_t(r)<<16)|(uint32_t(g)<<8)|b;}
    // V6 datasheet requires reset >280us; explicit idle guards the library frame.
    showPixels();
  }
}
