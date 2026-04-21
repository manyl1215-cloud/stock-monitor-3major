#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
資料儲存模組 - 儲存和讀取歷史資料
"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, List

logger = logging.getLogger(__name__)


class DataStorage:
    """資料儲存器 - 使用 JSON 格式儲存"""
    
    def __init__(self, data_dir='data'):
        self.data_dir = data_dir
        self.market_file = os.path.join(data_dir, 'market_history.json')
        self.stock_file = os.path.join(data_dir, 'stock_history.json')
        
        # 確保資料目錄存在
        os.makedirs(data_dir, exist_ok=True)
        
        # 初始化檔案
        self._init_file(self.market_file, [])
        self._init_file(self.stock_file, {})
    
    def _init_file(self, filepath: str, default_data):
        """初始化檔案（如果不存在）"""
        if not os.path.exists(filepath):
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(default_data, f, ensure_ascii=False, indent=2)
    
    def load_history(self) -> Dict:
        """
        載入歷史資料
        
        Returns:
            Dict: {
                'market': [...],  # 大盤歷史
                'stocks': {...}   # 個股歷史，按股票代號分組
            }
        """
        try:
            # 載入大盤歷史
            with open(self.market_file, 'r', encoding='utf-8') as f:
                market_history = json.load(f)
            
            # 載入個股歷史
            with open(self.stock_file, 'r', encoding='utf-8') as f:
                stock_history = json.load(f)
            
            logger.info(f"載入歷史資料: 大盤 {len(market_history)} 筆, 個股 {len(stock_history)} 檔")
            
            return {
                'market': market_history,
                'stocks': stock_history
            }
            
        except Exception as e:
            logger.error(f"載入歷史資料失敗: {str(e)}")
            return {
                'market': [],
                'stocks': {}
            }
    
    def save_data(self, market_data: Dict = None, stock_data: Dict = None):
        """
        儲存今日資料到歷史記錄
        
        Args:
            market_data: 大盤資料
            stock_data: 個股資料
        """
        timestamp = datetime.now().isoformat()
        
        try:
            # 儲存大盤資料
            if market_data:
                self._save_market_data(market_data, timestamp)
            
            # 儲存個股資料
            if stock_data:
                self._save_stock_data(stock_data, timestamp)
            
            logger.info("✅ 資料已儲存")
            
        except Exception as e:
            logger.error(f"儲存資料失敗: {str(e)}")
            raise
    
    def _save_market_data(self, market_data: Dict, timestamp: str):
        """儲存大盤資料"""
        # 讀取現有資料
        with open(self.market_file, 'r', encoding='utf-8') as f:
            history = json.load(f)
        
        # 加入新資料（插入到最前面）
        new_record = {
            **market_data,
            'timestamp': timestamp
        }
        history.insert(0, new_record)
        
        # 保留最近 365 天
        history = history[:365]
        
        # 寫回檔案
        with open(self.market_file, 'w', encoding='utf-8') as f:
            json.dump(history, f, ensure_ascii=False, indent=2)
        
        logger.info(f"大盤資料已儲存: {market_data['date']}")
    
    def _save_stock_data(self, stock_data: Dict, timestamp: str):
        """儲存個股資料"""
        # 讀取現有資料
        with open(self.stock_file, 'r', encoding='utf-8') as f:
            history = json.load(f)
        
        # 按股票代號分組儲存
        for stock in stock_data['stocks']:
            code = stock['code']
            
            if code not in history:
                history[code] = []
            
            # 加入新資料
            new_record = {
                **stock,
                'date': stock_data['date'],
                'timestamp': timestamp
            }
            history[code].insert(0, new_record)
            
            # 保留最近 365 天
            history[code] = history[code][:365]
        
        # 寫回檔案
        with open(self.stock_file, 'w', encoding='utf-8') as f:
            json.dump(history, f, ensure_ascii=False, indent=2)
        
        logger.info(f"個股資料已儲存: {len(stock_data['stocks'])} 檔")
    
    def get_stock_history(self, code: str, days: int = 30) -> List[Dict]:
        """
        取得特定股票的歷史資料
        
        Args:
            code: 股票代號
            days: 天數
        
        Returns:
            List[Dict]: 歷史資料列表
        """
        try:
            with open(self.stock_file, 'r', encoding='utf-8') as f:
                history = json.load(f)
            
            return history.get(code, [])[:days]
            
        except Exception as e:
            logger.error(f"讀取股票 {code} 歷史資料失敗: {str(e)}")
            return []
    
    def cleanup_old_data(self, days: int = 365):
        """清理過舊的資料"""
        try:
            # 清理大盤資料
            with open(self.market_file, 'r', encoding='utf-8') as f:
                market_history = json.load(f)
            
            market_history = market_history[:days]
            
            with open(self.market_file, 'w', encoding='utf-8') as f:
                json.dump(market_history, f, ensure_ascii=False, indent=2)
            
            # 清理個股資料
            with open(self.stock_file, 'r', encoding='utf-8') as f:
                stock_history = json.load(f)
            
            for code in stock_history:
                stock_history[code] = stock_history[code][:days]
            
            with open(self.stock_file, 'w', encoding='utf-8') as f:
                json.dump(stock_history, f, ensure_ascii=False, indent=2)
            
            logger.info(f"清理完成，保留最近 {days} 天資料")
            
        except Exception as e:
            logger.error(f"清理資料失敗: {str(e)}")


if __name__ == "__main__":
    # 測試
    logging.basicConfig(level=logging.INFO)
    storage = DataStorage('test_data')
    
    # 測試儲存
    market_data = {
        'date': '115/04/21',
        'foreign': 125.45,
        'trust': -23.18,
        'dealer': 8.92,
        'total': 111.19
    }
    
    stock_data = {
        'date': '1150421',
        'stocks': [
            {
                'code': '2330',
                'name': '台積電',
                'foreign': 1234.5,
                'trust': 234.5,
                'dealer': 123.4,
                'total': 1592.4
            }
        ]
    }
    
    storage.save_data(market_data, stock_data)
    
    # 測試讀取
    history = storage.load_history()
    print(f"大盤歷史: {len(history['market'])} 筆")
    print(f"個股歷史: {len(history['stocks'])} 檔")
    
    # 測試讀取特定股票
    stock_history = storage.get_stock_history('2330', 10)
    print(f"台積電歷史: {len(stock_history)} 筆")
