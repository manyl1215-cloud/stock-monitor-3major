#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速測試腳本 - 測試系統各項功能
"""

import os
import sys
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()

def test_environment():
    """測試環境變數設定"""
    print("=" * 60)
    print("測試 1: 環境變數檢查")
    print("=" * 60)
    
    required_vars = ['EMAIL_TO', 'SMTP_USER', 'SMTP_PASSWORD']
    all_ok = True
    
    for var in required_vars:
        value = os.getenv(var)
        if value:
            # 隱藏密碼
            display_value = '*' * 8 if 'PASSWORD' in var else value
            print(f"✅ {var}: {display_value}")
        else:
            print(f"❌ {var}: 未設定")
            all_ok = False
    
    if all_ok:
        print("\n✅ 環境變數設定完成！")
    else:
        print("\n❌ 請檢查 .env 檔案設定")
        sys.exit(1)
    
    return all_ok


def test_fetcher():
    """測試資料抓取"""
    print("\n" + "=" * 60)
    print("測試 2: 資料抓取測試")
    print("=" * 60)
    
    from modules.fetcher import TWSEFetcher
    
    fetcher = TWSEFetcher()
    
    print("\n測試大盤資料...")
    market_data = fetcher.fetch_market_data()
    
    if market_data:
        print(f"✅ 成功抓取大盤資料")
        print(f"   日期: {market_data['date']}")
        print(f"   外資: {market_data['foreign']:.2f} 億元")
        print(f"   投信: {market_data['trust']:.2f} 億元")
        print(f"   合計: {market_data['total']:.2f} 億元")
    else:
        print("❌ 無法抓取大盤資料（可能是假日）")
    
    print("\n測試個股資料 (台積電, 鴻海)...")
    stock_data = fetcher.fetch_stock_data(['2330', '2317'])
    
    if stock_data and stock_data['stocks']:
        print(f"✅ 成功抓取 {len(stock_data['stocks'])} 檔個股資料")
        for stock in stock_data['stocks']:
            print(f"   {stock['code']} {stock['name']}: 合計 {stock['total']:.0f} 張")
    else:
        print("❌ 無法抓取個股資料")
    
    return market_data, stock_data


def test_analyzer(market_data, stock_data):
    """測試分析功能"""
    print("\n" + "=" * 60)
    print("測試 3: 資料分析測試")
    print("=" * 60)
    
    from modules.analyzer import StockAnalyzer
    
    analyzer = StockAnalyzer()
    
    history = {'market': [], 'stocks': {}}
    analysis = analyzer.analyze(market_data, stock_data, history)
    
    if analysis['market']:
        print("✅ 大盤分析完成")
        if analysis['market']['alerts']:
            print(f"   警示數量: {len(analysis['market']['alerts'])}")
    
    if analysis['stocks']:
        print("✅ 個股分析完成")
        print(f"   超大額交易: {len(analysis['stocks']['large_trades_super'])} 檔")
        print(f"   大額交易: {len(analysis['stocks']['large_trades'])} 檔")
    
    return analysis


def test_storage():
    """測試資料儲存"""
    print("\n" + "=" * 60)
    print("測試 4: 資料儲存測試")
    print("=" * 60)
    
    from modules.storage import DataStorage
    
    storage = DataStorage('test_data')
    
    # 測試儲存
    test_market = {
        'date': '115/04/21',
        'foreign': 100.0,
        'trust': 50.0,
        'dealer': 10.0,
        'total': 160.0
    }
    
    storage.save_data(market_data=test_market)
    
    # 測試讀取
    history = storage.load_history()
    
    if history['market']:
        print(f"✅ 資料儲存成功")
        print(f"   大盤歷史: {len(history['market'])} 筆")
    else:
        print("❌ 資料儲存失敗")
    
    # 清理測試資料
    import shutil
    shutil.rmtree('test_data', ignore_errors=True)


def test_email():
    """測試 Email 發送"""
    print("\n" + "=" * 60)
    print("測試 5: Email 發送測試")
    print("=" * 60)
    
    from modules.emailer import EmailSender
    
    emailer = EmailSender()
    
    test_market = {
        'date': '115/04/21',
        'foreign': 125.45,
        'trust': -23.18,
        'dealer': 8.92,
        'total': 111.19
    }
    
    test_stocks = {'date': '1150421', 'stocks': []}
    
    test_analysis = {
        'market': {
            'today': test_market,
            'alerts': [],
            'trends': {}
        },
        'stocks': None
    }
    
    try:
        email_to = os.getenv('EMAIL_TO')
        print(f"\n準備發送測試 Email 至: {email_to}")
        print("這將發送一封真實的 Email，確定要繼續嗎？ (y/n): ", end='')
        
        response = input().lower()
        
        if response == 'y':
            emailer.send_report(
                email_to,
                test_market,
                test_stocks,
                test_analysis,
                'v2.0.0-test'
            )
            print("✅ Email 發送成功！請檢查信箱")
        else:
            print("⏭️  跳過 Email 發送測試")
    
    except Exception as e:
        print(f"❌ Email 發送失敗: {str(e)}")


def main():
    """主測試流程"""
    print("\n")
    print("╔═══════════════════════════════════════════════════════╗")
    print("║     三大法人監測系統 - 功能測試                       ║")
    print("╚═══════════════════════════════════════════════════════╝")
    print()
    
    # 測試 1: 環境變數
    if not test_environment():
        return
    
    # 測試 2: 資料抓取
    market_data, stock_data = test_fetcher()
    
    if not market_data and not stock_data:
        print("\n⚠️  無法抓取資料，可能是假日或非交易日")
        print("請在交易日的晚上 6 點後重新測試")
        return
    
    # 測試 3: 資料分析
    if market_data or stock_data:
        analysis = test_analyzer(market_data, stock_data)
    
    # 測試 4: 資料儲存
    test_storage()
    
    # 測試 5: Email 發送
    test_email()
    
    print("\n" + "=" * 60)
    print("測試完成！")
    print("=" * 60)
    print("\n如果所有測試都通過，系統已經準備就緒！")
    print("你可以執行 'python main.py' 來開始使用")
    print()


if __name__ == "__main__":
    main()
