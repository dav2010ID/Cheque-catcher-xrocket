import asyncio
import regex as re
import requests
from telethon import TelegramClient, events
from telethon.tl.functions.messages import RequestWebViewRequest
from telethon.tl.functions.messages import ImportChatInviteRequest
from telethon.tl.functions.channels import JoinChannelRequest
from telethon.tl.types import KeyboardButtonUrl
from concurrent.futures import ThreadPoolExecutor
from config import *
import os
import sys
import json
from datetime import datetime
from telethon.tl.types import KeyboardButtonCallback, KeyboardButton
from telethon.tl.functions.messages import GetBotCallbackAnswerRequest
import webbrowser
# Set the environment variable for the encoding
os.environ['PYTHONIOENCODING'] = 'utf-8'

# Alternatively, reconfigure stdout to use utf-8 encoding (Python 3.7+)
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding='utf-8')

client = TelegramClient(
    session='session', 
    api_id=int(api_id), 
    api_hash=api_hash,
    device_model=DEVICE_MODEL,
    system_version=SYSTEM_VERSION,
    app_version=APP_VERSION,
    lang_code=LANG_CODE,
    system_lang_code=SYSTEM_LANG_CODE
)

code_regex = re.compile(
    r"t\.me/(CryptoBot|send|tonRocketBot|CryptoTestnetBot|wallet|xrocket|xJetSwapBot)\?start="
    r"(CQ[A-Za-z0-9]{10}|C-[A-Za-z0-9]{10}|t_[A-Za-z0-9]{15}|mci_[A-Za-z0-9]{15}|mc_[A-Za-z0-9]{15}|c_[a-z0-9]{24})",
    re.IGNORECASE
)
url_regex = re.compile(r"https:\/\/t\.me\/\+(\w{12,})")
public_regex = re.compile(r"https:\/\/t\.me\/(\w{4,})")

replace_chars = ''' @#&+()*"'…;,!№•—–·±<{>}†★‡„“”«»‚‘’‹›¡¿‽~`|√π÷×§∆\\°^%©®™✓₤$₼€₸₾₶฿₳₥₦₫₿¤₲₩₮¥₽₻₷₱₧£₨¢₠₣₢₺₵₡₹₴₯₰₪'''
translation = str.maketrans('', '', replace_chars)

executor = ThreadPoolExecutor(max_workers=5)

crypto_black_list = []

global checks
global checks_count
global wallet
global captchas
global activated_checks
checks = []
wallet = []
channels = []
captchas = []
checks_count = 0
activated_checks = []
subscribed_channels=[]

rate_limit = 1  # delay in seconds to prevent being banned by Telegram
checks_file = 'activated_checks.json'
channels_file = 'subscribed_channels.json'

# Load activated checks from file
if os.path.exists(checks_file):
    with open(checks_file, 'r', encoding='utf-8') as f:
        activated_checks = json.load(f)
else:
    activated_checks = []

def save_channels():
    with open(channels_file, 'w', encoding='utf-8') as f:
        json.dump(subscribed_channels, f, ensure_ascii=False, indent=4)

@client.on(events.NewMessage(outgoing=True, pattern='.spam'))
async def handler(event):
    chat = event.chat if event.chat else (await event.get_chat())
    args = event.message.message.split(' ')
    for _ in range(int(args[1])):
        await client.send_message(chat, args[2])
        await asyncio.sleep(rate_limit)

def ocr_space_sync(file: bytes, overlay=False, language='eng', scale=True, OCREngine=2):
    payload = {
        'isOverlayRequired': overlay,
        'apikey': ocr_api_key,
        'language': language,
        'scale': scale,
        'OCREngine': OCREngine
    }
    response = requests.post(
        'https://api.ocr.space/parse/image',
        data=payload,
        files={'filename': ('image.png', file, 'image/png')}
    )
    result = response.json()
    return result.get('ParsedResults')[0].get('ParsedText').replace(" ", "")

async def ocr_space(file: bytes, overlay=False, language='eng'):
    loop = asyncio.get_running_loop()
    recognized_text = await loop.run_in_executor(
        executor, ocr_space_sync, file, overlay, language
    )
    return recognized_text

async def pay_out():
    await asyncio.sleep(86400)
    await client.send_message('CryptoBot', message=f'/wallet')
    await asyncio.sleep(rate_limit)
    messages = await client.get_messages('CryptoBot', limit=1)
    message = messages[0].message
    lines = message.split('\n\n')
    for line in lines:
        if ':' in line:
            if 'Доступно' in line:
                data = line.split('\n')[2].split('Доступно: ')[1].split(' (')[0].split(' ')
                summ = data[0]
                curency = data[1]
            else:
                data = line.split(': ')[1].split(' (')[0].split(' ')
                summ = data[0]
                curency = data[1]
            try:
                if summ == '0':
                    continue
                result = (await client.inline_query('send', f'{summ} {curency}'))[0]
                if 'Создать чек' in result.title:
                    await result.click(avto_vivod_tag)
                    await asyncio.sleep(rate_limit)
            except:
                pass

@client.on(events.NewMessage(chats=[1985737506], pattern="⚠️ Вы не можете активировать этот чек, так как вы не являетесь подписчиком канала"))
async def handle_new_message(event):
    global wallet
    code = None
    try:
        for row in event.message.reply_markup.rows:
            for button in row.buttons:
                try:
                    try:
                        check = code_regex.search(button.url)
                        if check:
                            code = check.group(2)
                    except:
                        pass
                    channel = url_regex.search(button.url)
                    public_channel = public_regex.search(button.url)
                    if channel:
                        await client(ImportChatInviteRequest(channel.group(1)))
                        await save_channel(channel.group(1))
                        await asyncio.sleep(rate_limit)
                    if public_channel:
                        await client(JoinChannelRequest(public_channel.group(1)))
                        await save_channel(public_channel.group(1))
                        await asyncio.sleep(rate_limit)

                except:
                    pass
    except AttributeError:
        pass
    if code and code not in wallet and code not in activated_checks:
        await client.send_message('wallet', message=f'/start {code}')
        wallet.append(code)
        activated_checks.append(code)
        await asyncio.sleep(rate_limit)
        save_checks()

@client.on(events.NewMessage(chats=[1559501630], pattern="Чтобы"))
async def handle_new_message(event):
    try:
        for row in event.message.reply_markup.rows:
            for button in row.buttons:
                try:
                    channel = url_regex.search(button.url)
                    if channel:
                        await client(ImportChatInviteRequest(channel.group(1)))
                        await asyncio.sleep(rate_limit)
                except:
                    pass
    except AttributeError:
        pass
    await event.message.click(data=b'check-subscribe')
    await asyncio.sleep(rate_limit)

@client.on(events.NewMessage(chats=[5014831088], pattern="To activate cheque"))
async def handle_new_message(event):
    try:
        for row in event.message.reply_markup.rows:
            for button in row.buttons:
                try:
                    channel = url_regex.search(button.url)
                    public_channel = public_regex.search(button.url)
                    if channel:
                        await client(ImportChatInviteRequest(channel.group(1)))
                        await asyncio.sleep(rate_limit)
                    if public_channel:
                        await client(JoinChannelRequest(public_channel.group(1)))
                        await asyncio.sleep(rate_limit)
                except:
                    pass
    except AttributeError:
        pass
    await asyncio.sleep(0.5)
    # Нажимаем на предпоследнюю кнопку
    try:
        if event.message.reply_markup and event.message.reply_markup.rows:
            # Получаем все кнопки в одном списке
            all_buttons = [button for row in event.message.reply_markup.rows for button in row.buttons]
            if len(all_buttons) >= 2:
                penultimate_button = all_buttons[-2]  # Предпоследняя кнопка
                if isinstance(penultimate_button, KeyboardButtonCallback):
                    await client(GetBotCallbackAnswerRequest(
                        peer=event.chat_id,
                        msg_id=event.message.id,
                        data=penultimate_button.data
                    ))
                elif isinstance(penultimate_button, KeyboardButton):
                    await client.send_message(event.chat_id, penultimate_button.text)
                print(f"Clicked button: {penultimate_button.text}")
    except AttributeError:
        pass
    await asyncio.sleep(rate_limit)

@client.on(events.NewMessage(chats=[5794061503]))
async def handle_new_message(event):
    try:
        for row in event.message.reply_markup.rows:
            for button in row.buttons:
                try:
                    try:
                        if (button.data.decode()).startswith(('showCheque_', 'activateCheque_')):
                            await event.message.click(data=button.data)
                            await asyncio.sleep(rate_limit)
                    except:
                        pass
                    channel = url_regex.search(button.url)
                    public_channel = public_regex.search(button.url)
                    if channel:
                        await client(ImportChatInviteRequest(channel.group(1)))
                        await asyncio.sleep(rate_limit)
                    if public_channel:
                        await client(JoinChannelRequest(public_channel.group(1)))
                        await asyncio.sleep(rate_limit)
                except:
                    pass
    except AttributeError:
        pass

async def filter(event):
    for word in ['You received', 'Вы обналичили чек на сумму:', '✅ Вы получили:', '💰 Вы получили']:
        if word in event.message.text:
            return True
    return False


@client.on(events.NewMessage(pattern="need to enter a password"))
async def handle_new_message(event):
    await client.send_message(channel, message=f'need pass for bot')


@client.on(events.NewMessage(chats=[5014831088],pattern="Complete a captcha, to prove that you are human"))
async def handle_new_message(event):
    requests.post("https://discord.com/api/webhooks/1256223658444062770/l17lwT_XvAjVBQfYo_dgUyZRPRhWIl-mT-A4tiTrF3lDXrV3AMd3SkgdPZacACROOfv0", json={"content":"new captha"})

    for row in event.message.reply_markup.rows:
            for button in row.buttons:

                if button.url:
                    peer = await client.get_input_entity('xrocket')  # Replace with your peer
                    result = await client(RequestWebViewRequest(
                        peer=peer,
                        bot=peer,
                        platform='android',
                        from_bot_menu=False,
                        url=button.url
                    ))
                    requests.post("https://discord.com/api/webhooks/1256223658444062770/l17lwT_XvAjVBQfYo_dgUyZRPRhWIl-mT-A4tiTrF3lDXrV3AMd3SkgdPZacACROOfv0", json={"content":result.url})
                    webbrowser.open(result.url)


@client.on(events.NewMessage(pattern="You already activated this multi-cheque"))
async def handle_new_message(event):
    print('You already activated this multi-cheque at time '+datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    await client.send_message(channel, message=f'You already activated this multi-cheque')

@client.on(events.NewMessage(pattern="This cheque only for users with Telegram Premium"))
async def handle_new_message(event):
    print(f'This cheque only for users with Telegram Premium. ')
    await client.send_message(channel, message=f'This cheque only for users with Telegram Premium. ')


@client.on(events.NewMessage(pattern="This multi-cheque already activated"))
async def handle_new_message(event):
    print(f'This multi-cheque already activated ')
    await client.send_message(channel, message=f'This multi-cheque already activated ')    

@client.on(events.MessageEdited(func=filter))
@client.on(events.NewMessage(func=filter))
async def handle_new_message(event):
    summ = event.raw_text.split('\n')[0].replace('You received ', '').replace('✅ Вы получили: ', '').replace('💰 Вы получили ', '').replace('Вы обналичили чек на сумму: ', '')
    global checks_count
    checks_count += 1
    await client.send_message(channel, message=f'✅ Активирован чек на сумму <b>{summ}</b>\nВсего чеков после запуска активировано: <b>{checks_count}</b>', parse_mode='HTML') 
    await asyncio.sleep(rate_limit)


@client.on(events.MessageEdited())
@client.on(events.NewMessage())
async def handle_new_message(event):
    global checks
    message_text = event.message.text.translate(translation)
    codes = code_regex.findall(message_text)
    if codes:
        print(codes)
        for bot_name, code in codes:
            if code not in checks and code not in activated_checks:
                await client.send_message(bot_name, message=f'/start {code}')
                checks.append(code)
                activated_checks.append(code)
                await asyncio.sleep(rate_limit)
                save_checks()
    try:
        for row in event.message.reply_markup.rows:
            for button in row.buttons:
                try:
                    match = code_regex.search(button.url)
                    if match and match.group(2) not in checks and match.group(2) not in activated_checks:
                        await client.send_message(match.group(1), message=f'/start {match.group(2)}')
                        checks.append(match.group(2))
                        activated_checks.append(match.group(2))
                        await asyncio.sleep(rate_limit)
                        save_checks()
                except AttributeError:
                    pass
    except AttributeError:
        pass

if anti_captcha:
    @client.on(events.NewMessage(chats=[1559501630], func=lambda e: e.photo))
    async def handle_photo_message(event):
        photo = await event.download_media(bytes)
        recognized_text = await ocr_space(file=photo)
        if recognized_text and recognized_text not in captchas:
            await client.send_message('CryptoBot', message=recognized_text)
            await asyncio.sleep(rate_limit)
            message = (await client.get_messages('CryptoBot', limit=1))[0].message
            if 'Incorrect answer.' in message or 'Неверный ответ.' in message:
                await client.send_message(channel, message=f'<b>❌ Не удалось разгадать каптчу, решите ее сами.</b>', parse_mode='HTML') 
                print(f'[!] Ошибка антикаптчи > Не удалось разгадать каптчу, решите ее сами.')
                captchas.append(recognized_text)
    print(f'[$] Антикаптча подключена!')

def save_checks():
    with open(checks_file, 'w', encoding='utf-8') as f:
        json.dump(activated_checks, f, ensure_ascii=False, indent=4)

async def save_channel(channel):
    if channel not in subscribed_channels:
        subscribed_channels.append(channel)
        save_channels()

async def main():
    try:
        await client.start()
        if avto_vivod and avto_vivod_tag:
            try:
                message = await client.send_message(avto_vivod_tag, message='1')
                await client.delete_messages(avto_vivod_tag, message_ids=[message.id])
                asyncio.create_task(pay_out())
                print(f'[$] Автовывод подключен!')
            except Exception as e:
                print(f'[!] Ошибка автовывода > Не удалось отправить тестовое сообщение на тег для авто вывода. Авто вывод отключен.')
        elif avto_vivod and not avto_vivod_tag:
            print(f'[!] Ошибка автовыводв > Вы не указали тег для авто вывода.')
        print(f'[$] Ловец чеков успешно запущен!')
        await client.run_until_disconnected()
    except Exception as e:
        print(f'[!] Ошибка коннекта > {e}')

asyncio.run(main())
