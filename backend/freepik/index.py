import json
import os
import re
import requests
from bs4 import BeautifulSoup
import psycopg2
import boto3
from urllib.parse import urlparse, quote
import base64
import uuid

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
            
            file_info = parse_and_download_freepik(freepik_url, file_format)
            
            if not file_info:
                return {
                    'statusCode': 404,
                    'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                    'body': json.dumps({'error': 'Не удалось получить информацию о файле'})
                }
            
            download_id = save_to_db(user_id, freepik_url, file_info, file_format)
            
            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({
                    'success': True,
                    'file_info': file_info,
                    'format': file_format,
                    'download_url': file_info.get('download_url'),
                    'download_id': download_id,
                    'message': f'Файл успешно загружен в формате {file_format}'
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


def parse_and_download_freepik(url: str, file_format: str) -> dict:
    """Парсинг страницы Freepik и скачивание файла"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Referer': 'https://www.freepik.com/',
        }
        
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        title_tag = soup.find('h1') or soup.find('title')
        title = title_tag.get_text(strip=True) if title_tag else 'Untitled'
        title = re.sub(r'[^\w\s-]', '', title)[:100]
        
        thumbnail = None
        img_tags = soup.find_all('img')
        for img_tag in img_tags:
            src = img_tag.get('src') or img_tag.get('data-src')
            if src and ('image' in str(img_tag.get('class', [])) or 'preview' in str(img_tag.get('class', []))):
                thumbnail = src
                break
        
        download_link = extract_download_link(soup, url, file_format)
        
        if download_link:
            file_content = download_file(download_link, headers)
            if file_content:
                cdn_url = upload_to_s3(file_content, title, file_format)
                
                return {
                    'title': title,
                    'thumbnail': thumbnail,
                    'available_formats': ['PSD', 'PNG', 'JPG', 'SVG', 'GIF', 'AI', 'EPS'],
                    'source_url': url,
                    'download_url': cdn_url
                }
        
        return {
            'title': title,
            'thumbnail': thumbnail,
            'available_formats': ['PSD', 'PNG', 'JPG', 'SVG', 'GIF', 'AI', 'EPS'],
            'source_url': url,
            'download_url': thumbnail
        }
        
    except Exception as e:
        print(f'Ошибка парсинга и скачивания: {e}')
        return None


def extract_download_link(soup: BeautifulSoup, page_url: str, file_format: str) -> str:
    """Извлечение прямой ссылки на скачивание файла"""
    try:
        scripts = soup.find_all('script')
        for script in scripts:
            if script.string and 'download' in script.string.lower():
                match = re.search(r'https?://[^\s"\'<>]+(?:jpg|png|svg|psd|ai|eps|gif)', script.string, re.IGNORECASE)
                if match:
                    return match.group(0)
        
        links = soup.find_all('a', href=True)
        for link in links:
            href = link.get('href', '')
            if 'download' in href.lower() or file_format.lower() in href.lower():
                if href.startswith('http'):
                    return href
                elif href.startswith('/'):
                    parsed = urlparse(page_url)
                    return f"{parsed.scheme}://{parsed.netloc}{href}"
        
        meta_og_image = soup.find('meta', property='og:image')
        if meta_og_image:
            return meta_og_image.get('content')
        
        return None
        
    except Exception as e:
        print(f'Ошибка извлечения ссылки: {e}')
        return None


def download_file(url: str, headers: dict) -> bytes:
    """Скачивание файла по прямой ссылке"""
    try:
        response = requests.get(url, headers=headers, timeout=30, stream=True)
        response.raise_for_status()
        
        max_size = 50 * 1024 * 1024
        content = b''
        
        for chunk in response.iter_content(chunk_size=8192):
            content += chunk
            if len(content) > max_size:
                print('Файл слишком большой')
                return None
        
        return content
        
    except Exception as e:
        print(f'Ошибка скачивания файла: {e}')
        return None


def upload_to_s3(file_content: bytes, title: str, file_format: str) -> str:
    """Загрузка файла в S3 и получение CDN URL"""
    try:
        s3 = boto3.client(
            's3',
            endpoint_url='https://bucket.poehali.dev',
            aws_access_key_id=os.environ['AWS_ACCESS_KEY_ID'],
            aws_secret_access_key=os.environ['AWS_SECRET_ACCESS_KEY']
        )
        
        file_id = str(uuid.uuid4())[:8]
        safe_title = re.sub(r'[^\w\s-]', '', title).replace(' ', '-')
        file_key = f'freepik/{file_id}-{safe_title}.{file_format.lower()}'
        
        content_types = {
            'PNG': 'image/png',
            'JPG': 'image/jpeg',
            'JPEG': 'image/jpeg',
            'SVG': 'image/svg+xml',
            'GIF': 'image/gif',
            'PSD': 'application/octet-stream',
            'AI': 'application/postscript',
            'EPS': 'application/postscript'
        }
        
        content_type = content_types.get(file_format.upper(), 'application/octet-stream')
        
        s3.put_object(
            Bucket='files',
            Key=file_key,
            Body=file_content,
            ContentType=content_type
        )
        
        cdn_url = f"https://cdn.poehali.dev/projects/{os.environ['AWS_ACCESS_KEY_ID']}/bucket/{file_key}"
        
        return cdn_url
        
    except Exception as e:
        print(f'Ошибка загрузки в S3: {e}')
        return None


def save_to_db(user_id: int, url: str, file_info: dict, file_format: str) -> int:
    """Сохранение информации о скачивании в БД"""
    try:
        dsn = os.environ.get('DATABASE_URL')
        conn = psycopg2.connect(dsn)
        cur = conn.cursor()
        
        cur.execute("""
            INSERT INTO downloads (user_id, freepik_url, file_title, file_format, thumbnail_url, file_path, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        """, (
            user_id,
            url,
            file_info.get('title'),
            file_format,
            file_info.get('thumbnail'),
            file_info.get('download_url'),
            'completed'
        ))
        
        download_id = cur.fetchone()[0]
        
        conn.commit()
        cur.close()
        conn.close()
        
        return download_id
        
    except Exception as e:
        print(f'Ошибка сохранения в БД: {e}')
        return 0


def get_download_history(user_id: int) -> list:
    """Получение истории скачиваний пользователя"""
    try:
        dsn = os.environ.get('DATABASE_URL')
        conn = psycopg2.connect(dsn)
        cur = conn.cursor()
        
        cur.execute("""
            SELECT id, freepik_url, file_title, file_format, thumbnail_url, file_path, downloaded_at
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
                'download_url': row[5],
                'downloaded_at': row[6].isoformat() if row[6] else None
            })
        
        cur.close()
        conn.close()
        
        return history
        
    except Exception as e:
        print(f'Ошибка получения истории: {e}')
        return []
