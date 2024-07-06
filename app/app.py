from flask import Flask
from binance.client import Client
from binance.exceptions import BinanceAPIException, BinanceOrderException
import time
from dotenv import load_dotenv
import os

app = Flask(__name__)

# .env 파일 로드
load_dotenv()

# 환경 변수에서 API 키와 시크릿을 가져옴
api_key = os.getenv('BINANCE_API_KEY')
api_secret = os.getenv('BINANCE_API_SECRET')

# 바이낸스 클라이언트 초기화 및 시간 동기화
client = Client(api_key, api_secret)

# 서버 시간 동기화 함수
def sync_time():
    server_time = client.get_server_time()
    client_time = server_time['serverTime'] - 1000  # 클라이언트 시간을 서버 시간보다 1초 늦게 설정
    client.timestamp_offset = client_time - int(time.time() * 1000)

# 시간 동기화
sync_time()

# 현물 계좌 잔고 조회 함수
def get_spot_account_balance():
    try:
        account_info = client.get_account()
        balances = account_info['balances']
        
        result = "현물 계좌 잔고:\n"
        for balance in balances:
            asset = balance['asset']
            free_balance = float(balance['free'])
            locked_balance = float(balance['locked'])
            
            if free_balance > 0 or locked_balance > 0:
                result += f"자산: {asset}, 사용 가능 잔고: {free_balance}, 잠긴 잔고: {locked_balance}\n"
        return result
    
    except BinanceAPIException as e:
        print(f"바이낸스 API 예외가 발생했습니다: {e}")
        return f"바이낸스 API 예외가 발생했습니다: {e}"
    except BinanceOrderException as e:
        print(f"바이낸스 주문 예외가 발생했습니다: {e}")
        return f"바이낸스 주문 예외가 발생했습니다: {e}"
    except Exception as e:
        print(f"예기치 않은 오류가 발생했습니다: {e}")
        return f"예기치 않은 오류가 발생했습니다: {e}"

# 선물 계좌 잔고 조회 함수
def get_futures_account_balance():
    try:
        account_info = client.futures_account()
        balances = account_info['assets']
        
        result = "선물 계좌 잔고:\n"
        for balance in balances:
            asset = balance['asset']
            wallet_balance = float(balance['walletBalance'])
            unrealized_profit = float(balance['unrealizedProfit'])
            
            if wallet_balance > 0 or unrealized_profit != 0:
                result += f"자산: {asset}, 지갑 잔고: {wallet_balance}, 미실현 손익: {unrealized_profit}\n"
        return result
    
    except BinanceAPIException as e:
        print(f"바이낸스 API 예외가 발생했습니다: {e}")
        return f"바이낸스 API 예외가 발생했습니다: {e}"
    except BinanceOrderException as e:
        print(f"바이낸스 주문 예외가 발생했습니다: {e}")
        return f"바이낸스 주문 예외가 발생했습니다: {e}"
    except Exception as e:
        print(f"예기치 않은 오류가 발생했습니다: {e}")
        return f"예기치 않은 오류가 발생했습니다: {e}"

# 현물 계좌 잔고 조회 엔드포인트
@app.route('/spot_balance', methods=['GET'])
def spot_balance():
    balances = get_spot_account_balance()
    return balances

# 선물 계좌 잔고 조회 엔드포인트
@app.route('/futures_balance', methods=['GET'])
def futures_balance():
    balances = get_futures_account_balance()
    return balances

if __name__ == '__main__':
    app.run(debug=True)
