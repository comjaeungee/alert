import ccxt
import pandas as pd
import ta
import requests
from datetime import datetime
import time

# 카카오톡 API 설정
KAKAO_API_URL = "https://kapi.kakao.com/v2/api/talk/memo/default/send"
KAKAO_API_KEY = "66395bd8f4016b700f53306f5ac2f3d7"  # 카카오 API 키 입력
KAKAO_USER_ID = "1286197"  # 카카오톡 오픈채팅 ID

# 비트겟 API 설정
exchange = ccxt.bitget({
    'apiKey': 'bg_ea7108650c92bb32f42dfcc8976239fb',
    'secret': 'c831257b449da3151e4839aa88d6242e9fee23407a8e6b24834d60c1f9c05c23',
    'enableRateLimit': True,
})

# 데이터 가져오기 함수
def fetch_data():
    ohlcv = exchange.fetch_ohlcv('BTC/USDT', timeframe='5m', limit=100)
    df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    df.set_index('timestamp', inplace=True)
    return df

# 볼린저밴드 분석
def analyze_bollinger(df):
    bb = ta.volatility.BollingerBands(close=df['close'], window=20, window_dev=2)
    df['bb_low'] = bb.bollinger_lband()
    df['bb_high'] = bb.bollinger_hband()
    
    # 볼린저밴드 하향 돌파 감지
    if df['close'].iloc[-1] < df['bb_low'].iloc[-1]:
        send_kakao_alert(df)

# 카카오톡 알림 보내기
def send_kakao_alert(df):
    message = f"📉 BTC 하락 알림!\n현재가: {df['close'].iloc[-1]:,.2f} USDT\n시간: {df.index[-1]}"
    
    # 카카오톡 API를 통해 메시지 전송
    headers = {
        "Authorization": f"Bearer {KAKAO_API_KEY}",
        "Content-Type": "application/x-www-form-urlencoded",
    }

    data = {
        "template_object": {
            "object_type": "text",
            "text": message,
            "link": {
                "web_url": "https://www.bitget.com",
                "mobile_web_url": "https://www.bitget.com"
            }
        }
    }

    response = requests.post(KAKAO_API_URL, headers=headers, json=data)
    
    if response.status_code == 200:
        print("카카오톡 알림 전송 성공!")
    else:
        print(f"카카오톡 알림 전송 실패: {response.status_code}")

# 프로그램 시작 시 알림
def send_startup_alert():
    message = "🚀 비트코인 봇이 시작되었습니다! 알림을 보내기 시작합니다."
    
    headers = {
        "Authorization": f"Bearer {KAKAO_API_KEY}",
        "Content-Type": "application/x-www-form-urlencoded",
    }

    data = {
        "template_object": {
            "object_type": "text",
            "text": message,
            "link": {
                "web_url": "https://www.bitget.com",
                "mobile_web_url": "https://www.bitget.com"
            }
        }
    }

    response = requests.post(KAKAO_API_URL, headers=headers, json=data)
    
    if response.status_code == 200:
        print("카카오톡 시작 알림 전송 성공!")
    else:
        print(f"카카오톡 시작 알림 전송 실패: {response.status_code}")

# 5분마다 실행
if __name__ == "__main__":
  
    # 프로그램 시작 시 알림 보내기
    send_startup_alert()
  
    while True:
        df = fetch_data()
        analyze_bollinger(df)
        time.sleep(300)  # 5분(300초)마다 실행

