# Xiaomi TV Backlight для Home Assistant

Интеграция добавляет управление подсветкой телевизора в Home Assistant.
Используйте её в автоматизациях для приглушения экрана ночью, например до 20%
после 23:00. Управление пультом через приложение также доступно.

На ТВ должно быть установлено [Xiaomi TV Backlight Control](https://github.com/alexshemr/xiaomi-tv-backlight-control)
с разрешением управления подсветкой. Для горячей кнопки на пульте включите
службу приложения в специальных возможностях.

## Настройка

1. Добавьте этот репозиторий в HACS → Пользовательские репозитории → **Integration**.
2. Установите интеграцию и перезапустите Home Assistant.
3. В приложении на ТВ откройте «Связать с Home Assistant».
4. В HA добавьте **Xiaomi TV Backlight Control**, выберите найденный телевизор
   или укажите его IP-адрес и введите шестизначный код с экрана ТВ.

Появятся сущность подсветки (0–100%) и датчик соединения.
Изменения с пульта отображаются в HA в течение 15 секунд.
Когда ТВ недоступен, подсветка показывает 0%, а датчик соединения выключается.

## Пример: приглушённый экран ночью

Пример устанавливает подсветку **20% в 23:00** или при восстановлении соединения
с ТВ ночью. Ночным периодом в примере считаются **23:00–07:00** по времени HA.
Замените оба идентификатора сущностей своими и при необходимости измените время окончания.

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

Проверено на **HA 2026.10.1, MiTV-MSSP1, Android TV 9, PI.5925**.

[English](README.md)
