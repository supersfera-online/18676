# Claude Code на Samsung Galaxy S22+

Пошаговая инструкция по установке Claude Code на телефон через Termux.

## Шаг 1: Установить Termux

**Важно:** Скачивайте Termux только с F-Droid, НЕ из Google Play (там устаревшая версия).

1. Откройте браузер на телефоне
2. Перейдите на https://f-droid.org/
3. Скачайте и установите F-Droid
4. В F-Droid найдите и установите **Termux**
5. Также установите **Termux:API** (для доступа к настройкам телефона)

## Шаг 2: Запустить установку

Откройте Termux и выполните по очереди:

```bash
# Скачать скрипт установки
pkg install -y git
git clone https://github.com/ВАШ_РЕПО/New.git
cd New

# Запустить установку
bash setup-termux.sh
```

Или вручную, если не хотите клонировать репо:

```bash
pkg update -y && pkg upgrade -y
pkg install -y nodejs-lts git python termux-api
npm install -g @anthropic-ai/claude-code
termux-setup-storage
```

## Шаг 3: Получить API-ключ

1. Перейдите на https://console.anthropic.com/
2. Зарегистрируйтесь / войдите
3. Перейдите в раздел API Keys
4. Создайте новый ключ
5. Скопируйте его

## Шаг 4: Запустить Claude Code

```bash
claude
```

При первом запуске введите API-ключ из шага 3.

## Что Claude Code может делать на телефоне

После установки Claude Code работает на телефоне так же, как на компьютере:

- Читать и редактировать файлы
- Запускать команды в терминале
- Работать с Git
- Писать и запускать скрипты

### Доступ к файлам телефона

```bash
# Фотографии
ls ~/storage/dcim/

# Загрузки
ls ~/storage/downloads/

# Документы
ls ~/storage/documents/
```

### Информация о телефоне (нужен Termux:API)

```bash
# Уровень батареи
termux-battery-status

# Информация о Wi-Fi
termux-wifi-connectioninfo

# Громкость
termux-volume

# Фонарик
termux-torch on
termux-torch off
```

## Решение проблем

### "Permission denied"
```bash
termux-setup-storage
```
Нажмите "Разрешить" во всплывающем окне.

### "npm: command not found"
```bash
pkg install -y nodejs-lts
```

### Claude Code не запускается
```bash
npm install -g @anthropic-ai/claude-code
```

### Мало места
```bash
# Проверить свободное место
df -h
# Очистить кэш npm
npm cache clean --force
```

## Советы

- Используйте **внешнюю клавиатуру** по Bluetooth для удобного набора
- Установите **Termux:Widget** чтобы запускать Claude Code одной кнопкой с рабочего стола
- Команда `termux-reload-settings` применяет изменения настроек Termux
