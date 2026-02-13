#!/usr/bin/env python3
"""Vinyl Vault - AI Image Recognition Service"""
import base64
import json
import time

def recognize_vinyl_image(image_data):
    """
    模擬 AI 辨識黑膠唱片
    實際應用中可以接 OpenAI Vision API 或 Google Cloud Vision
    """
    # 模擬延遲
    time.sleep(0.5)
    
    # 模擬資料庫比對結果
    mock_database = [
        {
            "title": "Dark Side of the Moon",
            "artist": "Pink Floyd",
            "year": 1973,
            "genre": "Rock",
            "label": "Harvest Records",
            "confidence": 0.96,
            "cover_emoji": "🎸",
            "description": "Pink Floyd 最經典的專輯之一，融合迷幻搖滾與前衛搖滾元素。"
        },
        {
            "title": "Abbey Road",
            "artist": "The Beatles",
            "year": 1969,
            "genre": "Rock",
            "label": "Apple Records",
            "confidence": 0.92,
            "cover_emoji": "🎸",
            "description": "The Beatles 解散前的經典之作，以其創新的錄音技術聞名。"
        },
        {
            "title": "Kind of Blue",
            "artist": "Miles Davis",
            "year": 1959,
            "genre": "Jazz",
            "label": "Columbia Records",
            "confidence": 0.94,
            "cover_emoji": "🎷",
            "description": "史上最暢銷的爵士專輯，被譽為 modal jazz 的代表作。"
        },
        {
            "title": "Rumours",
            "artist": "Fleetwood Mac",
            "year": 1977,
            "genre": "Rock",
            "label": "Warner Bros.",
            "confidence": 0.89,
            "cover_emoji": "🎸",
            "description": "Fleetwood Mac 最成功的專輯，融合搖滾與流行音樂元素。"
        },
        {
            "title": "Thriller",
            "artist": "Michael Jackson",
            "year": 1982,
            "genre": "Pop",
            "label": "Epic Records",
            "confidence": 0.91,
            "cover_emoji": "🕺",
            "description": "史上最暢銷的專輯，定義了流行舞曲的標準。"
        },
        {
            "title": "Random Access Memories",
            "artist": "Daft Punk",
            "year": 2013,
            "genre": "Electronic",
            "label": "Columbia Records",
            "confidence": 0.88,
            "cover_emoji": "🎹",
            "description": "Daft Punk 的第四張專輯，融合電子與放克音樂。"
        },
        {
            "title": "The Wall",
            "artist": "Pink Floyd",
            "year": 1979,
            "genre": "Rock",
            "label": "Harvest/Columbia",
            "confidence": 0.95,
            "cover_emoji": "🎸",
            "description": "Pink Floyd 的搖滾歌劇，探討疏離與隔離的主題。"
        },
        {
            "title": "Back to Black",
            "artist": "Amy Winehouse",
            "year": 2006,
            "genre": "R&B",
            "label": "Island Records",
            "confidence": 0.87,
            "cover_emoji": "🎤",
            "description": "Amy Winehouse 的第二張專輯，融合 soul 與 jazz 元素。"
        }
    ]
    
    import random
    result = random.choice(mock_database)
    result["estimated_price"] = round(random.uniform(20, 80), 2)
    result["estimated_value"] = round(random.uniform(40, 120), 2)
    
    return result

if __name__ == '__main__':
    print("Vinyl Recognition Service Ready!")
    print("Usage: Send base64 encoded image to /recognize endpoint")
