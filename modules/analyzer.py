#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
資料分析模組 - 分析三大法人買賣趨勢
"""

import logging
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class StockAnalyzer:
    """股市資料分析器"""
    
    def __init__(self):
        # 警示門檻設定
        self.thresholds = {
            'market_large': 50,      # 大盤大額買賣門檻（億元）
            'stock_large': 0.5,      # 個股大額買賣門檻（億元）
            'consecutive_days': 3    # 連續買賣天數門檻
        }
    
    def analyze(self, market_data: Dict, stock_data: Dict, history: Dict) -> Dict:
        """
        執行完整分析
        
        Args:
            market_data: 今日大盤資料
            stock_data: 今日個股資料
            history: 歷史資料
        
        Returns:
            Dict: 分析結果
        """
        analysis = {
            'market': None,
            'stocks': None
        }
        
        if market_data:
            analysis['market'] = self.analyze_market(market_data, history.get('market', []))
        
        if stock_data:
            analysis['stocks'] = self.analyze_stocks(stock_data, history.get('stocks', {}))
        
        return analysis
    
    def analyze_market(self, today_data: Dict, history_data: List[Dict]) -> Dict:
        """
        分析大盤三大法人資料
        
        Returns:
            Dict: {
                'today': {...},
                'alerts': [...],
                'trends': {...}
            }
        """
        analysis = {
            'today': today_data,
            'alerts': [],
            'trends': {}
        }
        
        # 檢查大額買賣
        if abs(today_data['foreign']) >= self.thresholds['market_large']:
            analysis['alerts'].append({
                'type': 'large_trade',
                'institution': '外資',
                'amount': today_data['foreign'],
                'message': f"外資{'大買' if today_data['foreign'] > 0 else '大賣'} {abs(today_data['foreign']):.2f} 億元"
            })
        
        if abs(today_data['trust']) >= self.thresholds['market_large']:
            analysis['alerts'].append({
                'type': 'large_trade',
                'institution': '投信',
                'amount': today_data['trust'],
                'message': f"投信{'大買' if today_data['trust'] > 0 else '大賣'} {abs(today_data['trust']):.2f} 億元"
            })
        
        # 分析連續買賣趨勢
        analysis['trends'] = {
            'foreign': self._analyze_trend('外資', today_data['foreign'], history_data, 'foreign'),
            'trust': self._analyze_trend('投信', today_data['trust'], history_data, 'trust'),
            'dealer': self._analyze_trend('自營商', today_data['dealer'], history_data, 'dealer')
        }
        
        return analysis
    
    def _analyze_trend(self, name: str, today_amount: float, 
                      history_data: List[Dict], field: str) -> Dict:
        """分析單一法人的連續買賣趨勢"""
        trend = {
            'name': name,
            'consecutive': 1,  # 包含今天
            'direction': 'buy' if today_amount > 0 else 'sell',
            'total_amount': today_amount
        }
        
        if not history_data:
            return trend
        
        # 計算連續買賣天數
        direction = today_amount > 0
        
        for day_data in history_data[:10]:  # 檢查最近10天
            day_amount = day_data.get(field, 0)
            if (day_amount > 0) == direction:
                trend['consecutive'] += 1
                trend['total_amount'] += day_amount
            else:
                break
        
        return trend
    
    def analyze_stocks(self, today_data: Dict, history_data: Dict) -> Dict:
        """
        分析個股三大法人資料
        
        Returns:
            Dict: {
                'large_trades_super': [...],
                'large_trades': [...],
                'consecutive_buys': [...],
                'consecutive_sells': [...]
            }
        """
        analysis = {
            'large_trades_super': [],  # 超大額交易
            'large_trades': [],         # 大額交易
            'consecutive_buys': [],     # 連續買超
            'consecutive_sells': []     # 連續賣超
        }
        
        for stock in today_data['stocks']:
            # 粗估金額（假設股價100元）
            estimated_amount = abs(stock['total']) * 100 / 10000  # 億元
            
            # 檢查大額交易
            if estimated_amount >= self.thresholds['stock_large'] * 3:
                analysis['large_trades_super'].append({
                    **stock,
                    'amount': estimated_amount,
                    'type': 'buy' if stock['total'] > 0 else 'sell'
                })
            elif estimated_amount >= self.thresholds['stock_large']:
                analysis['large_trades'].append({
                    **stock,
                    'amount': estimated_amount,
                    'type': 'buy' if stock['total'] > 0 else 'sell'
                })
            
            # 檢查連續買賣
            history = history_data.get(stock['code'], [])
            consecutive = self._check_consecutive_trade(stock, history)
            
            if consecutive['days'] >= self.thresholds['consecutive_days']:
                if consecutive['direction'] == 'buy':
                    analysis['consecutive_buys'].append({
                        **stock,
                        'consecutive': consecutive
                    })
                else:
                    analysis['consecutive_sells'].append({
                        **stock,
                        'consecutive': consecutive
                    })
        
        # 排序
        analysis['large_trades_super'].sort(key=lambda x: abs(x['total']), reverse=True)
        analysis['large_trades'].sort(key=lambda x: abs(x['total']), reverse=True)
        analysis['consecutive_buys'].sort(key=lambda x: x['consecutive']['days'], reverse=True)
        analysis['consecutive_sells'].sort(key=lambda x: x['consecutive']['days'], reverse=True)
        
        return analysis
    
    def _check_consecutive_trade(self, stock: Dict, history: List[Dict]) -> Dict:
        """檢查個股連續買賣"""
        result = {
            'days': 1,
            'direction': 'buy' if stock['total'] > 0 else 'sell',
            'total_amount': stock['total']
        }
        
        if not history:
            return result
        
        direction = stock['total'] > 0
        
        for day_data in history[:20]:  # 檢查最近20天
            day_total = day_data.get('total', 0)
            if (day_total > 0) == direction:
                result['days'] += 1
                result['total_amount'] += day_total
            else:
                break
        
        return result


if __name__ == "__main__":
    # 測試
    analyzer = StockAnalyzer()
    
    # 測試資料
    market_data = {
        'date': '115/04/21',
        'foreign': 125.45,
        'trust': -23.18,
        'dealer': 8.92,
        'total': 111.19
    }
    
    history = {
        'market': [
            {'foreign': 100.0, 'trust': -20.0, 'dealer': 10.0},
            {'foreign': 80.0, 'trust': -15.0, 'dealer': 5.0},
        ]
    }
    
    result = analyzer.analyze_market(market_data, history['market'])
    print("市場分析結果:")
    print(f"警示: {result['alerts']}")
    print(f"趨勢: {result['trends']}")
