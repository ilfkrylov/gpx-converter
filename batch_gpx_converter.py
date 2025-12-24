#!/usr/bin/env python3
"""
Пакетный конвертер закладок Яндекс Карт в GPX.
Читает список URL из файла и использует настройки из переменных окружения.
"""

import os
import sys
import subprocess
import logging
from pathlib import Path

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

def main():
    # Загружаем переменные окружения из .env, если файл существует
    from dotenv import load_dotenv
    load_dotenv()
    
    # Получаем путь к папке для сохранения из переменной окружения
    output_dir = os.environ.get("OUTPUT_DIR")
    if not output_dir:
        logging.error("Переменная окружения OUTPUT_DIR не установлена.")
        logging.info("Добавьте OUTPUT_DIR в .env файл или экспортируйте в системе.")
        sys.exit(1)
    
    # Проверяем существование папки
    if not os.path.isdir(output_dir):
        logging.error(f"Папка '{output_dir}' не существует.")
        sys.exit(1)
    
    # Получаем путь к файлу со списком URL
    if len(sys.argv) != 2:
        logging.error("Использование: python batch_gpx_converter.py <файл_с_URL>")
        logging.info("  <файл_с_URL> - текстовый файл, где каждая строка содержит один URL")
        sys.exit(1)
    
    url_list_path = sys.argv[1]
    if not os.path.isfile(url_list_path):
        logging.error(f"Файл '{url_list_path}' не найден.")
        sys.exit(1)
    
    # Читаем URL из файла
    with open(url_list_path, 'r', encoding='utf-8') as f:
        urls = [line.strip() for line in f if line.strip() and not line.startswith('#')]
    
    if not urls:
        logging.warning("Файл не содержит URL.")
        sys.exit(0)
    
    logging.info(f"Найдено {len(urls)} URL для обработки.")
    
    # Получаем путь к основному скрипту
    script_dir = Path(__file__).parent
    main_script = script_dir / "gpx_converter.py"
    if not main_script.exists():
        logging.error(f"Основной скрипт '{main_script}' не найден.")
        sys.exit(1)
    
    # API ключ из переменных окружения
    api_key = os.environ.get("YANDEX_GEOCODER_API_KEY")
    api_key_arg = f"--api_key {api_key}" if api_key else ""
    
    # Обрабатываем каждый URL
    success_count = 0
    for i, url in enumerate(urls, 1):
        logging.info(f"[{i}/{len(urls)}] Обработка: {url}")
        
        # Формируем команду
        cmd = [
            sys.executable,
            str(main_script),
            url,
            output_dir,
        ]
        if api_key:
            cmd.extend(["--api_key", api_key])
        
        # Запускаем
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='ignore'
            )
            if result.returncode == 0:
                logging.info(f"[{i}/{len(urls)}] Успешно обработан: {url}")
                success_count += 1
            else:
                logging.error(f"[{i}/{len(urls)}] Ошибка при обработке {url}:")
                if result.stderr:
                    for line in result.stderr.split('\n'):
                        if line.strip():
                            logging.error(f"  {line}")
        except Exception as e:
            logging.error(f"[{i}/{len(urls)}] Исключение при запуске: {e}")
    
    logging.info(f"Обработка завершена. Успешно: {success_count}/{len(urls)}")

if __name__ == "__main__":
    main()
