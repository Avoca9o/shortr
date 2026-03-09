# shortr

## Описание API

### Базовый функционал

Обычный CRUD над ссылками:
* POST /links/shorten
request: curl -X POST localhost:8000/links/shorten?url=https://market.yandex.ru/card/korzina-dlya-belya-gryaznogo-khraneniya-organayzer-dlya-vannoy-seraya/101998257428?do-waremd5=aWkXkorJGlG-tEhuxyhzJA&cpc=q_jrvQoN_LWQxQsnfwIAWVz8CcnnX60whH_cDcT9Y8V1WXPC_-R7z1uD2_uK4Nkg8IxpyIXsK2Xs--m66N7_MBhBw73uUkyhCH9y80mXZyX6YErd0urjM_J1oDhPxtasCxwtfvrQL8dSx470Ik2_bjuG5no3qcDladeiL2eff2zKM0xC6fMKECHAqMlnbauZR4e59h5Gc4KeyKeKMKg3cZyPl1jShwIRwzMSiN_URyE%2C&ogV=-12
response:
{
    "short_url": "http://localhost:8000/links/BF1jZC5yopRzCA"
}
* GET /links/{short_url}
Нажать на ссылку, полученную в POST /links/shorten -- убедиться, что открывается нужная страничка
* DELETE /links/{short_url}
request: curl -X DELETE http://localhost:8000/links/BF1jZC5yopRzCA
response:
{
    "message": "Link deleted successfully"
}
* PUT /links/{short_url}
{
    "message": "Link updated successfully"
}

Получение статистики по ссылке:
* GET /links/{short_url}/stats
request: curl -X GET http://localhost:8000/links/PPTaqLe8nc2pJg/stats
{
    "original_url": "https://market.yandex.ru/card/korzina-dlya-belya-gryaznogo-khraneniya-organayzer-dlya-vannoy-seraya/101998257428?do-waremd5=aWkXkorJGlG-tEhuxyhzJA",
    "created_at": "2026-03-09T22:10:26.388549",
    "access_count": 6,
    "last_accessed_at": "2026-03-09T22:10:26.388554"
}

Создание ссылок с кастомным алиасом:
* POST /links/shorten?custom_alias={alias}
curl -X POST localhost:8000/links/shorten?url=https://market.yandex.ru/card/korzina-dlya-belya-gryaznogo-khraneniya-organayzer-dlya-vannoy-seraya/101998257428?do-waremd5=aWkXkorJGlG-tEhuxyhzJA&cpc=q_jrvQoN_LWQxQsnfwIAWVz8CcnnX60whH_cDcT9Y8V1WXPC_-R7z1uD2_uK4Nkg8IxpyIXsK2Xs--m66N7_MBhBw73uUkyhCH9y80mXZyX6YErd0urjM_J1oDhPxtasCxwtfvrQL8dSx470Ik2_bjuG5no3qcDladeiL2eff2zKM0xC6fMKECHAqMlnbauZR4e59h5Gc4KeyKeKMKg3cZyPl1jShwIRwzMSiN_URyE%2C&ogV=-12&custom_alias=my-alias
{
    "short_url": "http://localhost:8000/links/my-alias"
}

Поиск ссылки по оригинальному url:
* GET /links/search?original_url={url}
curl -X GET http://localhost:8000/links/search?original_url=https://market.yandex.ru/card/korzina-dlya-belya-gryaznogo-khraneniya-organayzer-dlya-vannoy-seraya/101998257428?do-waremd5=aWkXkorJGlG-tEhuxyhzJA&cpc=q_jrvQoN_LWQxQsnfwIAWVz8CcnnX60whH_cDcT9Y8V1WXPC_-R7z1uD2_uK4Nkg8IxpyIXsK2Xs--m66N7_MBhBw73uUkyhCH9y80mXZyX6YErd0urjM_J1oDhPxtasCxwtfvrQL8dSx470Ik2_bjuG5no3qcDladeiL2eff2zKM0xC6fMKECHAqMlnbauZR4e59h5Gc4KeyKeKMKg3cZyPl1jShwIRwzMSiN_URyE%2C&ogV=-12
{
    "short_url": "http://localhost:8000/links/avoca9o3"
}

Указание времени жизни ссылки:
* POST /links/shorten?expires_at={date}
curl -X POST localhost:8000/links/shorten?url=https://market.yandex.ru/card/korzina-dlya-belya-gryaznogo-khraneniya-organayzer-dlya-vannoy-seraya/101998257428?do-waremd5=aWkXkorJGlG-tEhuxyhzJA&cpc=q_jrvQoN_LWQxQsnfwIAWVz8CcnnX60whH_cDcT9Y8V1WXPC_-R7z1uD2_uK4Nkg8IxpyIXsK2Xs--m66N7_MBhBw73uUkyhCH9y80mXZyX6YErd0urjM_J1oDhPxtasCxwtfvrQL8dSx470Ik2_bjuG5no3qcDladeiL2eff2zKM0xC6fMKECHAqMlnbauZR4e59h5Gc4KeyKeKMKg3cZyPl1jShwIRwzMSiN_URyE%2C&ogV=-12&custom_alias=my-alias-2&expires_at=2026-03-09T22:59:26
{
    "short_url": "http://localhost:8000/links/my-alias-2"
}
Сначала корректно переходит, потом {"error":"Link expired"}

Регистрация пользоваателя:
* POST /auth/register?username={name}&password={pass}
request: curl -X POST http://localhost:8000/auth/register?username=avoca9o5&password=qwerty123
{
    "message": "User created successfully"
}

Получение токена:
* POST /auth/login?username={name}&password={pass}
request: curl -X POST http://localhost:8000/auth/login?username=avoca9o5&password=qwerty123
{
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjo3fQ.uX2Hpms0erkmRqPnqVlQO-rNuC_rX8k-2CPglniaKlc"
}

### Дополнительный функционал

Получение списка топ-10 самых популярных ссылок:
* GET /links/top-10
request: curl -X GET http://localhost:8000/links/top-10
{
    "links": [
        {
            "short_url": "Y_IR2LMTVWKjBA",
            "original_url": "https://www.ozon.ru/product/lukum-orehovyy-assorti-500-gramm-650235959/?at=pZtpLz0VrsBlEAWrT6glrPJfGANKQmTokM3gLhQl2wkR",
            "access_count": 13
        },
        {
            "short_url": "T6c7_S_WqG8fpg",
            "original_url": "https://www.ozon.ru/product/lukum-orehovyy-assorti-500-gramm-650235959/?at=pZtpLz0VrsBlEAWrT6glrPJfGANKQmTokM3gLhQl2wkR",
            "access_count": 7
        },
        {
            "short_url": "PPTaqLe8nc2pJg",
            "original_url": "https://market.yandex.ru/card/korzina-dlya-belya-gryaznogo-khraneniya-organayzer-dlya-vannoy-seraya/101998257428?do-waremd5=aWkXkorJGlG-tEhuxyhzJA",
            "access_count": 6
        },
        {
            "short_url": "avoca9o",
            "original_url": "https://market.yandex.ru/card/korzina-dlya-belya-gryaznogo-khraneniya-organayzer-dlya-vannoy-seraya/101998257428?do-waremd5=aWkXkorJGlG-tEhuxyhzJA",
            "access_count": 6
        },
        {
            "short_url": "avoca9o2",
            "original_url": "https://market.yandex.ru/card/korzina-dlya-belya-gryaznogo-khraneniya-organayzer-dlya-vannoy-seraya/101998257428?do-waremd5=aWkXkorJGlG-tEhuxyhzJA",
            "access_count": 5
        },
        {
            "short_url": "tDYBLEotGqNDrw",
            "original_url": "https://market.yandex.ru/card/korzina-dlya-belya-gryaznogo-khraneniya-organayzer-dlya-vannoy-seraya/101998257428?do-waremd5=aWkXkorJGlG-tEhuxyhzJA",
            "access_count": 5
        },
        {
            "short_url": "my-alias-2",
            "original_url": "https://market.yandex.ru/card/korzina-dlya-belya-gryaznogo-khraneniya-organayzer-dlya-vannoy-seraya/101998257428?do-waremd5=aWkXkorJGlG-tEhuxyhzJA",
            "access_count": 1
        },
        {
            "short_url": "3TzHHWdBm3o96g",
            "original_url": "https://market.yandex.ru/card/korzina-dlya-belya-gryaznogo-khraneniya-organayzer-dlya-vannoy-seraya/101998257428?do-waremd5=aWkXkorJGlG-tEhuxyhzJA",
            "access_count": 1
        },
        {
            "short_url": "8bOKyLeAycd0Nw",
            "original_url": "https://market.yandex.ru/card/korzina-dlya-belya-gryaznogo-khraneniya-organayzer-dlya-vannoy-seraya/101998257428?do-waremd5=aWkXkorJGlG-tEhuxyhzJA",
            "access_count": 1
        },
        {
            "short_url": "BF1jZC5yopRzCA",
            "original_url": "https://market.yandex.ru/card/korzina-dlya-belya-gryaznogo-khraneniya-organayzer-dlya-vannoy-seraya/101998257428?do-waremd5=aWkXkorJGlG-tEhuxyhzJA",
            "access_count": 1
        }
    ]
}

Получение qrcode вместо сырой ссылки:
* POST /links/{short_url}?qrcode=True
request: curl -X POST localhost:8000/links/shorten?url=https://market.yandex.ru/card/korzina-dlya-belya-gryaznogo-khraneniya-organayzer-dlya-vannoy-seraya/101998257428?do-waremd5=aWkXkorJGlG-tEhuxyhzJA&cpc=q_jrvQoN_LWQxQsnfwIAWVz8CcnnX60whH_cDcT9Y8V1WXPC_-R7z1uD2_uK4Nkg8IxpyIXsK2Xs--m66N7_MBhBw73uUkyhCH9y80mXZyX6YErd0urjM_J1oDhPxtasCxwtfvrQL8dSx470Ik2_bjuG5no3qcDladeiL2eff2zKM0xC6fMKECHAqMlnbauZR4e59h5Gc4KeyKeKMKg3cZyPl1jShwIRwzMSiN_URyE%2C&ogV=-12&qrcode=True
Возвращается файлом, можно отсканировать и перейти (в случае с localhost только вырезать ножницами и отправлять картинку в соответствующие сервисы, которые умеют расшифровывать qrcode)

## Описание БД
* В качестве постоянной базы данных использовал postgres
* Для кэширования использовал redis
* И то, и другое, развернул на отдельно арендованной виртуальной машике (данные для подключения приложил в anytask вместе с заданием, чтобы не светить в публичном репозитории)

## Инструкция по запуску
* Достаточно создать .env файл по примеру .env_example (данные для БД и редиса в anytask) и запустить приложенный Dockerfile
docker build -t shortr .

docker run -d \
  --name shortr \
  --env-file .env \
  -p 80:8000 \
  shortr
