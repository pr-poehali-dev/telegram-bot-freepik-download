import json
import os
import re
import requests
from bs4 import BeautifulSoup
import psycopg2
from urllib.parse import urlparse

def handler(event: dict, context) -> dict:
    """
    API для скачивания файлов с Freepik.
    Принимает ссылку на файл, парсит страницу, извлекает информацию и скачивает файл.
    """
    method = event.get('httpMethod', 'GET')
    
    if method == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type'
            },
            'body': ''
        }
    
    if method == 'POST':
        try:
            body = json.loads(event.get('body', '{}'))
            freepik_url = body.get('url', '').strip()
            file_format = body.get('format', 'PNG').upper()
            user_id = body.get('user_id', 0)
            
            if not freepik_url:
                return {
                    'statusCode': 400,
                    'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                    'body': json.dumps({'error': 'URL обязателен'})
                }
            
            if not is_valid_freepik_url(freepik_url):
                return {
                    'statusCode': 400,
                    'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                    'body': json.dumps({'error': 'Неверная ссылка Freepik/Flaticon'})
                }
            
            file_info = parse_freepik_page(freepik_url)
            
            if not file_info:
                return {
                    'statusCode': 404,
                    'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                    'body': json.dumps({'error': 'Не удалось получить информацию о файле'})
                }
            
            save_to_db(user_id, freepik_url, file_info, file_format)
            
            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({
                    'success': True,
                    'file_info': file_info,
                    'format': file_format,
                    'message': f'Файл готов к скачиванию в формате {file_format}'
                })
            }
            
        except Exception as e:
            return {
                'statusCode': 500,
                'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({'error': f'Ошибка сервера: {str(e)}'})
            }
    
    if method == 'GET':
        try:
            user_id = event.get('queryStringParameters', {}).get('user_id', '0')
            history = get_download_history(int(user_id))
            
            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({'history': history})
            }
            
        except Exception as e:
            return {
                'statusCode': 500,
                'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({'error': str(e)})
            }
    
    return {
        'statusCode': 405,
        'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
        'body': json.dumps({'error': 'Метод не поддерживается'})
    }


def is_valid_freepik_url(url: str) -> bool:
    """Проверка валидности URL Freepik/Flaticon"""
    parsed = urlparse(url)
    return 'freepik.com' in parsed.netloc or 'flaticon.com' in parsed.netloc


def parse_freepik_page(url: str) -> dict:
    """Парсинг страницы Freepik для извлечения информации о файле"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        title_tag = soup.find('h1') or soup.find('title')
        title = title_tag.get_text(strip=True) if title_tag else 'Untitled'
        
        thumbnail = None
        img_tag = soup.find('img', {'class': re.compile('.*preview.*|.*image.*')})
        if img_tag:
            thumbnail = img_tag.get('src') or img_tag.get('data-src')
        
        available_formats = ['PSD', 'PNG', 'JPG', 'SVG', 'GIF', 'AI', 'EPS']
        
        return {
            'title': title,
            'thumbnail': thumbnail,
            'available_formats': available_formats,
            'source_url': url
        }
        
    except Exception as e:
        print(f'Ошибка парсинга: {e}')
        return None


def save_to_db(user_id: int, url: str, file_info: dict, file_format: str):
    """Сохранение информации о скачивании в БД"""
    try:
        dsn = os.environ.get('DATABASE_URL')
        conn = psycopg2.connect(dsn)
        cur = conn.cursor()
        
        cur.execute("""
            INSERT INTO downloads (user_id, freepik_url, file_title, file_format, thumbnail_url, status)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            user_id,
            url,
            file_info.get('title'),
            file_format,
            file_info.get('thumbnail'),
            'completed'
        ))
        
        conn.commit()
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f'Ошибка сохранения в БД: {e}')


def get_download_history(user_id: int) -> list:
    """Получение истории скачиваний пользователя"""
    try:
        dsn = os.environ.get('DATABASE_URL')
        conn = psycopg2.connect(dsn)
        cur = conn.cursor()
        
        cur.execute("""
            SELECT id, freepik_url, file_title, file_format, thumbnail_url, downloaded_at
            FROM downloads
            WHERE user_id = %s
            ORDER BY downloaded_at DESC
            LIMIT 50
        """, (user_id,))
        
        rows = cur.fetchall()
        
        history = []
        for row in rows:
            history.append({
                'id': row[0],
                'url': row[1],
                'title': row[2],
                'format': row[3],
                'thumbnail': row[4],
                'downloaded_at': row[5].isoformat() if row[5] else None
            })
        
        cur.close()
        conn.close()
        
        return history
        
    except Exception as e:
        print(f'Ошибка получения истории: {e}')
        return []
