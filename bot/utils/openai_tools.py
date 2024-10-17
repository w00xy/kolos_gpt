import http
import os
from os import getenv

import httpx
from dotenv import load_dotenv
from httpx import AsyncClient
from openai import AsyncOpenAI
from typing import List, Tuple

load_dotenv()


async def load_proxies_from_url(url: str):
    headers = {
        "accept": "*/*",
        "accept-encoding": "gzip, deflate, br, zstd",
        "accept-language": "en-GB,en;q=0.9,en-US;q=0.8,ru;q=0.7",
        "origin": "https://proxyscrape.com",
        "priority": "u=1, i",
        "referer": "https://proxyscrape.com/",
        "sec-ch-ua": '"Microsoft Edge";v="129", "Not=A?Brand";v="8", "Chromium";v="129"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-site",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36 Edg/129.0.0.0"
    }
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)
        if response.status_code == 200:
            proxies = response.text.splitlines()  # Разделяем по строкам
            return proxies
        else:
            print(f"Не удалось получить список прокси: статус {response.status_code}")
            return []


def load_proxies(file_path: str) -> List[str]:
    with open(file_path, 'r') as file:
        proxies = [line.strip() for line in file.readlines()]
    return proxies


# Функция для создания HTTP-клиента с указанным прокси
def create_openai_client_with_proxy(proxy_url: str):
    return AsyncOpenAI(
        api_key=os.getenv("OPENAI_API_KEY"),
        http_client=httpx.AsyncClient(proxies=proxy_url)
    )


def create_openai_client():
    return AsyncOpenAI(
        api_key=os.getenv("OPENAI_API_KEY")
    )

# Класс для работы с OpenAI
class OpenAiTools:
    @staticmethod
    async def get_chatgpt(start: int, messages: List[Tuple[int, str, str, int]], proxies: List[str] = None):
        mess = [
            {"role": "system",
             "content": "Ты — агроном-консультант. Твоя задача — предоставлять фермерам профессиональные "
                        "советы по удобрениям, защите растений, управлению урожайностью и другим аспектам агрономии. "
                        "Предоставляй три варианта решения проблемы: минимальные затраты, "
                        "оптимальный вариант и максимальная эффективность."}
        ]
        for i in range(start, len(messages)):
            mess.append({"role": messages[i][1], "content": messages[i][2]})

        if proxies:
            # Пробуем каждый прокси
            for proxy_url in proxies:
                try:
                    # Создаем клиента OpenAI с прокси
                    client = create_openai_client_with_proxy(proxy_url)

                    # Отправляем запрос к OpenAI
                    response = await client.chat.completions.create(
                        messages=mess,
                        model="gpt-4o-mini",
                        max_tokens=16384,
                        temperature=1,
                    )

                    # Возвращаем результат, если запрос успешен
                    return response.choices[0].message.content

                except Exception as e:
                    print(f"Ошибка при использовании прокси {proxy_url}: {e}")
                    continue  # Пробуем следующий прокси, если ошибка
        else:
            try:
                # Создаем клиента OpenAI с прокси
                client = create_openai_client()

                # Отправляем запрос к OpenAI
                response = await client.chat.completions.create(
                    messages=mess,
                    model="gpt-4o-mini",
                    max_tokens=16384,
                    temperature=1,
                )

                # Возвращаем результат, если запрос успешен
                return response.choices[0].message.content
            except Exception as e:
                print(f"Ошибка при отправлении запроса: {e}")
                return None

        return "Не удалось выполнить запрос через прокси."
