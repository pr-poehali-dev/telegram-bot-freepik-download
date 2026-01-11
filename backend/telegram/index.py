import json
import os
import requests
import psycopg2

TELEGRAM_API = 'https://api.telegram.org/bot{token}/{method}'

def handler(event: dict, context) -> dict:
    """
    Telegram Bot webhook для обработки сообщений от пользователей.
    Принимает ссылку на Freepik, скачивает файл и отправляет пользователю.
    """
    method = event.get('httpMethod', 'POST')
    
    if method == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'POST, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type'
            },
            'body': ''
        }
    
    if method == 'POST':
        try:
            body = json.loads(event.get('body', '{}'))
            
            if 'message' not in body:
                return {'statusCode': 200, 'body': 'OK'}
            
            message = body['message']
            chat_id = message['chat']['id']
            text = message.get('text', '').strip()
            
            if text.startswith('/start'):
                send_welcome_message(chat_id)
                return {'statusCode': 200, 'body': 'OK'}
            
            if 'freepik.com' in text or 'flaticon.com' in text:
                handle_freepik_url(chat_id, text)
                return {'statusCode': 200, 'body': 'OK'}
            
            send_message(chat_id, 'Отправь мне ссылку на файл с Freepik или Flaticon 🚀')
            return {'statusCode': 200, 'body': 'OK'}
            
        except Exception as e:
            print(f'Ошибка обработки webhook: {e}')
            return {'statusCode': 500, 'body': str(e)}
    
    return {
        'statusCode': 405,
        'headers': {'Content-Type': 'application/json'},
        'body': json.dumps({'error': 'Метод не поддерживается'})
    }


def send_welcome_message(chat_id: int):
    """Отправка приветственного сообщения"""
    text = """🎨 Привет! Я Freepik Bot

Отправь мне ссылку на премиум-файл с Freepik или Flaticon, и я скачаю его бесплатно!

📎 Поддерживаемые форматы:
• PSD • PNG • JPG • SVG • GIF • AI • EPS

Просто отправь ссылку, и я всё сделаю! 🚀"""
    
    send_message(chat_id, text)


def handle_freepik_url(chat_id: int, url: str):
    """Обработка ссылки на Freepik"""
    try:
        send_message(chat_id, '🔍 Ищу файл...')
        
        file_info = parse_freepik_file(url)
        
        if not file_info:
            send_message(chat_id, '❌ Не удалось найти файл. Проверь ссылку.')
            return
        
        formats_text = ' • '.join(file_info.get('available_formats', ['PNG']))
        message = f"""✅ Файл найден!

📁 {file_info.get('title', 'Без названия')}
📦 Форматы: {formats_text}

Выбери формат для скачивания:"""
        
        send_message_with_formats(chat_id, message, file_info.get('available_formats', ['PNG']), url)
        
        save_user_request(chat_id, url, file_info)
        
    except Exception as e:
        print(f'Ошибка обработки URL: {e}')
        send_message(chat_id, f'❌ Ошибка: {str(e)}')


def send_message(chat_id: int, text: str):
    """Отправка текстового сообщения"""
    token = os.environ.get('TELEGRAM_BOT_TOKEN')
    if not token:
        print('TELEGRAM_BOT_TOKEN не установлен')
        return
    
    url = TELEGRAM_API.format(token=token, method='sendMessage')
    payload = {
        'chat_id': chat_id,
        'text': text,
        'parse_mode': 'HTML'
    }
    
    requests.post(url, json=payload)


def send_message_with_formats(chat_id: int, text: str, formats: list, url: str):
    """Отправка сообщения с кнопками выбора формата"""
    token = os.environ.get('TELEGRAM_BOT_TOKEN')
    if not token:
        return
    
    keyboard = []
    row = []
    for i, fmt in enumerate(formats):
        row.append({
            'text': fmt,
            'callback_data': f'download:{fmt}:{url}'
        })
        if (i + 1) % 3 == 0:
            keyboard.append(row)
            row = []
    
    if row:
        keyboard.append(row)
    
    api_url = TELEGRAM_API.format(token=token, method='sendMessage')
    payload = {
        'chat_id': chat_id,
        'text': text,
        'reply_markup': {
            'inline_keyboard': keyboard
        }
    }
    
    requests.post(api_url, json=payload)


def parse_freepik_file(url: str) -> dict:
    """Получение информации о файле через API парсинга"""
    try:
        response = requests.post(
            'YOUR_BACKEND_URL/freepik',
            json={'url': url, 'user_id': 0},
            timeout=15
        )
        
        if response.status_code == 200:
            data = response.json()
            return data.get('file_info')
        
        return None
        
    except Exception as e:
        print(f'Ошибка парсинга через API: {e}')
        return {
            'title': 'Файл Freepik',
            'available_formats': ['PNG', 'JPG', 'SVG', 'PSD']
        }


def save_user_request(chat_id: int, url: str, file_info: dict):
    """Сохранение запроса пользователя в БД"""
    try:
        dsn = os.environ.get('DATABASE_URL')
        conn = psycopg2.connect(dsn)
        cur = conn.cursor()
        
        cur.execute("""
            INSERT INTO downloads (user_id, freepik_url, file_title, file_format, status)
            VALUES (%s, %s, %s, %s, %s)
        """, (
            chat_id,
            url,
            file_info.get('title'),
            'pending',
            'pending'
        ))
        
        conn.commit()
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f'Ошибка сохранения запроса: {e}')
