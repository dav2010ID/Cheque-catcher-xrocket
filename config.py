api_id = ''
api_hash = ''
# Инструкция по получению: https://telegra.ph/Sozdayom-paru-api-idhash-dlya-lovca-chekov-11-03

DEVICE_MODEL = "PC 64bit"
SYSTEM_VERSION = "Windows 10"
APP_VERSION = "4.6"
LANG_CODE = "ru"
SYSTEM_LANG_CODE = "ru-RU"

channel = 'lovecchkov' # Айди канала с логами об активированных чеках. Если вы хотите указать публичный канал, то введите 'тег без @', Например channel = 'lovec_checkov'

avto_vivod = True # Если данные параметр True, то скрипт раз в сутки будет переводить деньги с помощью чека на указанный аккаунт. Чтобы отключить укажите False, например avto_vivod = False
avto_vivod_tag = 'kekusername' # Тег аккаунта(без @), куда раз в сутки будет отправляться чек со всеми собранными средствами. Например avto_vivod_tag = 'absolutely_enough'

avto_otpiska = True # Если данные параметр True, то скрипт будет автоматически выходить из каналов, которе не публиковали чеки в течении суток. Чтобы отключить укажите False, например avto_otpiska = False

anti_captcha = True # Если параметр True, то скрипт будет автоматически разгадывать каптчу для CryptoBot. Чтобы отключить укажите False, например anti_captcha = False

ocr_api_key = '' # Инструкция по получению: https://telegra.ph/Poluchenie-OCR-API-KEY-11-03

# https://t.me/lovec_checkov