# Xiaomi TV Backlight for Home Assistant

This integration adds a TV backlight control to Home Assistant. Use it in
automations to reduce the screen brightness at night, for example to 20% after
23:00. Remote control remains available through the TV app.

Requires [Xiaomi TV Backlight Control](https://github.com/alexshemr/xiaomi-tv-backlight-control)
installed on the TV with backlight permission. Enable its accessibility service
to use the remote shortcut.

## Setup

1. Add this repository in HACS → Custom repositories → **Integration**.
2. Install it and restart Home Assistant.
3. In the TV app, open **Pair with Home Assistant**.
4. In HA, add **Xiaomi TV Backlight Control**, select the discovered TV or enter
   its IP address, and enter the six-digit code shown on the TV.

The integration creates a backlight number (0–100%) and a connection sensor.
Changes made with the remote appear in HA within 15 seconds.
When the TV is unreachable, the number shows 0% and the connection sensor turns off.

## Example: dim the screen at night

This example sets backlight to **20% at 23:00**, or when the TV reconnects during
the night. The example night period is **23:00–07:00**, using HA local time.
Replace both entity IDs with yours and adjust the end time if needed.

```yaml
alias: TV backlight at night
triggers:
  - trigger: time
    at: "23:00:00"
  - trigger: state
    entity_id: binary_sensor.xiaomi_tv_connection
    to: "on"
conditions:
  - condition: time
    after: "23:00:00"
    before: "07:00:00"
  - condition: state
    entity_id: binary_sensor.xiaomi_tv_connection
    state: "on"
actions:
  - action: number.set_value
    target:
      entity_id: number.xiaomi_tv_backlight
    data:
      value: 20
mode: single
```

Tested on **HA 2026.10.1, MiTV-MSSP1, Android TV 9, PI.5925**.

[Русский](README.ru.md)
