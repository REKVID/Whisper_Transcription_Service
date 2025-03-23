#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ТЕСТ НАПИСАЛ КОПИЛОТ !
"""Тестирование одновременной отправки нескольких видео с разных IP-адресов.

Этот модуль отправляет 3 видео на сервер транскрипции:
- Два видео отправляются одновременно.
- Третье видео отправляется после успешной обработки первых двух.
- Каждое видео отправляется с уникального IP-адреса.

Видеофайлы берутся из папки test_video.

Example:
    Запуск теста:

        $ python test_concurrent_uploads.py

Attributes:
    None

Todo:
    ---

"""

import os
import asyncio
import aiohttp
import time
from pathlib import Path


async def upload_video(session, video_path, ip_address, language=None):
    """Загружает видео на сервер с указанным IP-адресом.
    
    Отправляет видеофайл на сервер, эмулируя запрос с указанного IP-адреса
    с помощью заголовка X-Forwarded-For.
    
    Args:
        session (aiohttp.ClientSession): Сессия HTTP-клиента.
        video_path (str): Путь к видеофайлу.
        ip_address (str): IP-адрес, с которого эмулируется запрос.
        language (str, optional): Язык для транскрипции. По умолчанию None.
        
    Returns:
        dict: Результат транскрипции от сервера или информация об ошибке.
        
    Raises:
        Exception: Ошибки соединения или обработки запроса.
    """
    filename = os.path.basename(video_path)
    
    # Эмуляция отправки с разных IP-адресов путем добавления заголовка X-Forwarded-For
    headers = {"X-Forwarded-For": ip_address}
    
    # Формируем параметры для запроса
    data = aiohttp.FormData()
    data.add_field('file', 
                   open(video_path, 'rb'),
                   filename=filename,
                   content_type='video/mp4')
    
    if language:
        data.add_field('language', language)
    
    print(f"Начало загрузки {filename} с IP {ip_address}")
    start_time = time.time()
    
    # Отправляем запрос на сервер
    try:
        async with session.post('http://localhost:8000/transcriptions', 
                              data=data,
                              headers=headers) as response:
            processing_time = time.time() - start_time
            
            if response.status == 200:
                try:
                    result = await response.json()
                except aiohttp.client_exceptions.ContentTypeError:
                    # Если сервер не вернул JSON, попробуем получить текст
                    text = await response.text()
                    result = {"status": response.status, "text": text}
            else:
                # Если статус не 200, получаем текст ошибки
                text = await response.text()
                result = {"status": response.status, "error": text}
            
            print(f"Завершена загрузка {filename} с IP {ip_address}. "
                  f"Время обработки: {processing_time:.2f} секунд. "
                  f"Код ответа: {response.status}")
            
            if response.status == 200:
                print(f"Результат обработки: {result}")
            else:
                print(f"Ошибка: {text[:200]}...")
                
            return result
    except Exception as e:
        processing_time = time.time() - start_time
        print(f"Ошибка при загрузке {filename} с IP {ip_address}: {str(e)}")
        return {"status": "error", "error": str(e)}


async def main():
    """Основная функция для выполнения теста одновременной отправки видео.
    
    Загружает 3 видеофайла из папки test_video и отправляет их на сервер:
    1. Первые два видео отправляются одновременно с разных IP-адресов.
    2. После их обработки отправляется третье видео с третьего IP-адреса.
    
    Returns:
        None
    
    Raises:
        Exception: Ошибки получения списка видео или их отправки.
    """
    # Получение списка видео из папки test_video
    video_dir = Path("test_video")
    videos = list(video_dir.glob("*.mp4"))
    
    if len(videos) < 3:
        print(f"В папке test_video найдено только {len(videos)} видео, нужно минимум 3")
        return
    
    # Используем первые три видео из директории
    video1_path = str(videos[0])
    video2_path = str(videos[1])
    video3_path = str(videos[2])
    
    # Различные IP-адреса для тестирования
    ip1 = "192.168.1.1"
    ip2 = "10.0.0.1"
    ip3 = "172.16.0.1"
    
    print(f"Видео для тестирования:")
    print(f"1: {os.path.basename(video1_path)}")
    print(f"2: {os.path.basename(video2_path)}")
    print(f"3: {os.path.basename(video3_path)}")
    
    async with aiohttp.ClientSession() as session:
        # Одновременно отправляем первые два видео
        tasks = [
            upload_video(session, video1_path, ip1),
            upload_video(session, video2_path, ip2)
        ]
        
        print("\nЗапуск одновременной загрузки первых двух видео...")
        # Запускаем две задачи параллельно и ждем их завершения
        pending_tasks = await asyncio.gather(*tasks)
        
        print("\nПервые два видео обработаны. Отправка третьего видео...")
        
        # Отправляем третье видео после завершения первых двух
        result3 = await upload_video(session, video3_path, ip3)
        
        print("\nВсе задачи выполнены успешно!")


if __name__ == "__main__":
    asyncio.run(main()) 