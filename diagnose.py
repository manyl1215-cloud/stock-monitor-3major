#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速診斷腳本 - 測試證交所資料抓取
"""

import requests
from datetime import datetime, timedelta

def test_twse_connection():
    """測試證交所連線"""
    print("=" * 60)
    print("台灣證券交易所連線測試")
    print("=" * 60)
    
    # 測試最近 5 天
    for days_ago in range(5):
        test_date = datetime.now() - timedelta(days=days_ago)
        roc_year = test_date.year - 1911
        roc_date = f"{roc_year}{test_date.month:02d}{test_date.day:02d}"
        
        print(f"\n【測試 Day {days_ago}】{test_date.strftime('%Y-%m-%d')} (民國 {roc_date})")
        print("-" * 60)
        
        # 測試大盤資料
        url = f"https://www.twse.com.tw/rwd/zh/fund/BFI82U?response=json&date={roc_date}"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json',
        }
        
        try:
            print(f"URL: {url}")
            response = requests.get(url, headers=headers, timeout=30)
            print(f"狀態碼: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"JSON stat: {data.get('stat', '無')}")
                
                if data.get('stat') == 'OK' and data.get('data'):
                    print(f"✅ 成功！資料筆數: {len(data['data'])}")
                    
                    # 顯示第一筆資料
                    if data['data']:
                        first = data['data'][0]
                        print(f"\n第一筆資料:")
                        print(f"  欄位數量: {len(first)}")
                        print(f"  日期: {first[0] if len(first) > 0 else '無'}")
                        print(f"  外資: {first[1] if len(first) > 1 else '無'}")
                        print(f"  投信: {first[2] if len(first) > 2 else '無'}")
                    
                    print("\n🎉 找到有效資料！")
                    return True
                else:
                    print(f"⚠️  回應無資料 (stat={data.get('stat')})")
            
            elif response.status_code == 307:
                print("❌ 307 重定向 - 可能被安全機制阻擋")
                print(f"回應內容: {response.text[:200]}")
            
            else:
                print(f"❌ HTTP 錯誤 {response.status_code}")
                print(f"回應內容: {response.text[:200]}")
        
        except requests.exceptions.Timeout:
            print("❌ 連線逾時")
        
        except requests.exceptions.ConnectionError:
            print("❌ 連線失敗")
        
        except Exception as e:
            print(f"❌ 錯誤: {str(e)}")
    
    print("\n" + "=" * 60)
    print("❌ 最近 5 天都沒有找到有效資料")
    print("=" * 60)
    
    print("\n可能原因:")
    print("1. 證交所網站維護中")
    print("2. 連續假期（需等到下個交易日）")
    print("3. IP 被封鎖（GitHub Actions 的 IP）")
    print("4. 執行時間太早（資料尚未更新）")
    
    return False

if __name__ == "__main__":
    test_twse_connection()
