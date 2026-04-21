#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
資料抓取模組 - 從證交所抓取三大法人資料
"""

import requests
import time
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, List

logger = logging.getLogger(__name__)


class TWSEFetcher:
    """台灣證券交易所資料抓取器"""
    
    def __init__(self):
        self.session = requests.Session()
        # 設定 Headers 模擬瀏覽器
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Language': 'zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7',
            'X-Requested-With': 'XMLHttpRequest'
        })
        
        # API URLs
        self.market_url = 'https://www.twse.com.tw/rwd/zh/fund/BFI82U'
        self.stock_url = 'https://www.twse.com.tw/rwd/zh/fund/T86'
    
    def _get_roc_date(self, date=None):
        """轉換為民國日期格式 YYYMMDD"""
        if date is None:
            date = datetime.now()
        
        roc_year = date.year - 1911
        return f"{roc_year}{date.month:02d}{date.day:02d}"
    
    def _fetch_with_retry(self, url, params, max_retries=3):
        """帶重試機制的請求"""
        for attempt in range(max_retries):
            try:
                # 設定 Referer
                if 'BFI82U' in url:
                    self.session.headers['Referer'] = 'https://www.twse.com.tw/zh/page/trading/fund/BFI82U.html'
                else:
                    self.session.headers['Referer'] = 'https://www.twse.com.tw/zh/page/trading/fund/T86.html'
                
                response = self.session.get(url, params=params, timeout=30)
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get('stat') == 'OK' and data.get('data'):
                        return data
                    else:
                        logger.warning(f"回應無資料: stat={data.get('stat')}")
                else:
                    logger.warning(f"HTTP 錯誤 {response.status_code}")
                
                # 等待後重試
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)  # 指數退避
                    
            except Exception as e:
                logger.warning(f"請求失敗 (嘗試 {attempt + 1}/{max_retries}): {str(e)}")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)
        
        return None
    
    def fetch_market_data(self) -> Optional[Dict]:
        """
        抓取大盤三大法人買賣資料
        
        Returns:
            Dict: {
                'date': '115/04/21',
                'foreign': 123.45,  # 億元
                'trust': 23.45,
                'dealer': 12.34,
                'total': 159.24
            }
        """
        logger.info("抓取大盤三大法人資料...")
        
        # 嘗試最近 5 天
        for days_ago in range(5):
            test_date = datetime.now() - timedelta(days=days_ago)
            roc_date = self._get_roc_date(test_date)
            
            logger.info(f"嘗試日期: {test_date.strftime('%Y-%m-%d')} (民國 {roc_date})")
            
            params = {
                'response': 'json',
                'date': roc_date
            }
            
            data = self._fetch_with_retry(self.market_url, params)
            
            if data and data.get('data'):
                # 解析資料
                # 格式: [日期, 外資, 投信, 自營商(自行買賣), 自營商(避險), 合計]
                row = data['data'][0]
                
                result = {
                    'date': row[0],
                    'foreign': float(row[1].replace(',', '')) / 100000000,  # 轉億元
                    'trust': float(row[2].replace(',', '')) / 100000000,
                    'dealer': (float(row[3].replace(',', '')) + float(row[4].replace(',', ''))) / 100000000,
                    'total': float(row[5].replace(',', '')) / 100000000
                }
                
                logger.info(f"✅ 成功抓取大盤資料: {result['date']}")
                logger.info(f"   外資: {result['foreign']:.2f}億, 投信: {result['trust']:.2f}億, 合計: {result['total']:.2f}億")
                
                return result
            
            logger.info(f"該日期無資料，繼續嘗試...")
        
        logger.warning("最近5天都沒有找到大盤資料")
        return None
    
    def fetch_stock_data(self, watch_list: List[str] = None) -> Optional[Dict]:
        """
        抓取個股三大法人買賣資料
        
        Args:
            watch_list: 監測股票代號列表，None 表示全部
        
        Returns:
            Dict: {
                'date': '1150421',
                'stocks': [
                    {
                        'code': '2330',
                        'name': '台積電',
                        'foreign': 1234.5,  # 張
                        'trust': 234.5,
                        'dealer': 123.4,
                        'total': 1592.4
                    },
                    ...
                ]
            }
        """
        logger.info("抓取個股三大法人資料...")
        
        # 嘗試最近 5 天
        for days_ago in range(5):
            test_date = datetime.now() - timedelta(days=days_ago)
            roc_date = self._get_roc_date(test_date)
            
            logger.info(f"嘗試日期: {test_date.strftime('%Y-%m-%d')} (民國 {roc_date})")
            
            params = {
                'response': 'json',
                'date': roc_date
            }
            
            data = self._fetch_with_retry(self.stock_url, params)
            
            if data and data.get('data'):
                stocks = []
                
                for row in data['data']:
                    # 格式: [代號, 名稱, 外資, 投信, 自營商(自行買賣), 自營商(避險), 合計]
                    code = row[0].strip()
                    name = row[1].strip()
                    
                    # 過濾監測清單
                    if watch_list and code not in watch_list:
                        continue
                    
                    stocks.append({
                        'code': code,
                        'name': name,
                        'foreign': float(row[2].replace(',', '')) / 1000,  # 轉張數
                        'trust': float(row[3].replace(',', '')) / 1000,
                        'dealer': (float(row[4].replace(',', '')) + float(row[5].replace(',', ''))) / 1000,
                        'total': float(row[6].replace(',', '')) / 1000
                    })
                
                logger.info(f"✅ 成功抓取個股資料: {len(stocks)} 檔股票")
                
                return {
                    'date': roc_date,
                    'stocks': stocks
                }
            
            logger.info(f"該日期無資料，繼續嘗試...")
        
        logger.warning("最近5天都沒有找到個股資料")
        return None


if __name__ == "__main__":
    # 測試
    logging.basicConfig(level=logging.INFO)
    fetcher = TWSEFetcher()
    
    print("\n測試大盤資料:")
    market = fetcher.fetch_market_data()
    print(market)
    
    print("\n測試個股資料 (台積電、鴻海):")
    stocks = fetcher.fetch_stock_data(['2330', '2317'])
    print(stocks)
