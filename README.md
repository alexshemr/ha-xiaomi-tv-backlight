# Xiaomi TV Backlight for Home Assistant

Control Xiaomi TV backlight from Home Assistant automations.
For example, lower it when sleep mode starts.

Requires the [TV app](https://github.com/alexshemr/xiaomi-tv-backlight-control).

## Setup

1. Add this repository in HACS → Custom repositories → **Integration**.
2. Install it and restart Home Assistant.
3. On the TV, open **Pair with Home Assistant**.
4. Add **Xiaomi TV Backlight Control** in HA and enter the code from the TV.

Creates a backlight number (0–100%) and a connection sensor.
Updates every 15 seconds. When the TV is offline, the number shows 0%.

## Sleep automation

Replace the entity IDs with yours.

```yaml
alias: Dim TV for sleep
triggers:
  - trigger: state
    entity_id: input_boolean.sleep_mode
    to: "on"
conditions:
  - condition: state
    entity_id: binary_sensor.xiaomi_tv_connection
    state: "on"
actions:
  - action: number.set_value
    target:
      entity_id: number.xiaomi_tv_backlight
    data:
      value: 0
```

Tested on **HA 2026.10.1, MiTV-MSSP1, Android TV 9, PI.5925**.

[Русский](README.ru.md)
