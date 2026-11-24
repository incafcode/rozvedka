# Rozvedka 5.0.4 — Локальная сборка / Local Build

[🇷🇺 Русский](#-русский) | [🇬🇧 English](#-english)

---

## 🇷🇺 Русский

**Смысл софта:** парсинг с различных карт для вайбкодеров. Собирает потенциальных покупателей и выдает всю информацию по социальным сетям для связи, также можно подвязать свой ИИ по API. Программа уже имеет весь необходимый функционал — доделывать её смысла нет, поэтому дописывать или ломать более новые версии не вижу смысла.

### Как ставить:
1. Ставим `Rozvedka-Setup-5.0.4.exe` (обычный установщик: *Далее -> Далее*).
2. Запускаем `patch.bat` и ждем надписи **«готово»**.
3. Программа откроется сама, в дальнейшем можно запускать с ярлыка.

### Что делает патч:
- Убирает вход и подписку.
- Включает встроенный интерфейс (работает без их сайта).
- Поиск работает через **OpenStreetMap**, ключи не нужны.
- Если вставить свой ключ **Google Places** в настройках — появятся рейтинги и отзывы.
- **2ГИС** и облако не трогает (они работают на стороне сервера).

### Что в папке:
- `patcher.py` — патчит уже установленный `app-5.0.4.asar`.
- `ready\app-5.0.4.asar` — готовый пропатченный файл (если не установлен Python).
- `patch.bat` — автоматически выберет способ патчинга.
- `restore.bat` — вернет оригинальный файл.
- `start.bat` — просто запускает программу.

### Требования и примечания:
- **Python 3.8+** нужен только для работы `patcher.py`. Если Python не установлен, `patch.bat` сам возьмет готовый файл из папки `ready` — ничего дополнительно ставить не надо.
- Если программа обновилась и файл изменился — патч может не встать. В таком случае запустите `restore.bat` и ждите обновления патча.
- В комплекте предоставляю **все исходники (сурсы)** на доработку программы — вы можете полностью видеть всё, что находится внутри. Пользуйтесь!

> *Вайбкод софт обязан быть бесплатным*  
> **by [t.me/xomatroll](https://t.me)**

---

## 🇬🇧 English

**About the software:** Map scraping tool for vibecoders. It collects potential leads/customers and provides all their social media contact details, with the ability to connect your own AI via API. The program already includes all the necessary features—there is no point in adding to it, so I see no reason to modify or crack newer versions.

### How to install:
1. Run `Rozvedka-Setup-5.0.4.exe` (standard installer: *Next -> Next*).
2. Run `patch.bat` and wait for the **"done" ("готово")** message.
3. The program will launch automatically; after that, you can use the desktop shortcut.

### What the patch does:
- Removes login and subscription checks.
- Enables the built-in interface (works independently without their website).
- Search works via **OpenStreetMap** (no API keys required).
- Adding your own **Google Places** API key in the settings enables ratings and reviews.
- Does not touch **2GIS** or cloud features (those are server-side).

### Folder contents:
- `patcher.py` — patches the already installed `app-5.0.4.asar`.
- `ready\app-5.0.4.asar` — pre-patched file (used if Python is not installed).
- `patch.bat` — automatically selects the patching method.
- `restore.bat` — restores the original file.
- `start.bat` — simply launches the application.

### Requirements & Notes:
- **Python 3.8+** is only required to run `patcher.py`. If you don't have Python, `patch.bat` will automatically use the pre-patched file from the `ready` folder—no extra installations needed.
- If the app updates and the core file changes, the patch might not apply. In that case, run `restore.bat` and wait for a patch update.
- **All source files** are included in the archive for further customization—you can inspect everything inside the program. Enjoy!

> *Vibecode software must be free*  
> **by [t.me/xomatroll](https://t.me)**
