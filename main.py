#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
三大法人買賣監測系統 - Python 版本
Taiwan Stock Institutional Investors Monitor

版本：v2.0.0
更新日期：2026-04-21
作者：Claude AI Assistant
"""

import os
import sys
import logging
from datetime import datetime, timedelta
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()

# 匯入自訂模組
from modules.fetcher import TWSEFetcher
from modules.analyzer import StockAnalyzer
from modules.emailer import EmailSender
from modules.storage import DataStorage

# 設定日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('stock_monitor.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class StockMonitor:
    """三大法人監測系統主類別"""
    
    def __init__(self):
        self.version = "v2.0.0"
        self.fetcher = TWSEFetcher()
        self.analyzer = StockAnalyzer()
        self.emailer = EmailSender()
        self.storage = DataStorage()
        
        # 從環境變數讀取設定
        self.email_to = os.getenv('EMAIL_TO', 'manyl1215@gmail.com')
        self.watch_list = self._parse_watch_list(os.getenv('WATCH_LIST', ''))
        
        logger.info(f"系統啟動 - {self.version}")
        logger.info(f"收件人: {self.email_to}")
    
    def _parse_watch_list(self, watch_list_str):
        """解析監測股票清單"""
        if not watch_list_str:
            return []
        return [code.strip() for code in watch_list_str.split(',') if code.strip()]
    
    def run(self):
        """執行主流程"""
        try:
            logger.info("="*60)
            logger.info(f"開始執行三大法人監測 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            logger.info("="*60)
            
            # 檢查 Telegram 設定
            if not self.emailer.bot_token:
                error_msg = "❌ 錯誤：未設定 TELEGRAM_BOT_TOKEN"
                logger.error(error_msg)
                logger.error("請在 GitHub Secrets 中設定 TELEGRAM_BOT_TOKEN")
                logger.error("或在 .env 檔案中設定")
                raise ValueError(error_msg)
            
            if not self.emailer.chat_id:
                error_msg = "❌ 錯誤：未設定 TELEGRAM_CHAT_ID"
                logger.error(error_msg)
                logger.error("請在 GitHub Secrets 中設定 TELEGRAM_CHAT_ID")
                logger.error("或在 .env 檔案中設定")
                raise ValueError(error_msg)
            
            logger.info(f"✅ Telegram 設定正常")
            logger.info(f"   Bot Token: {self.emailer.bot_token[:20]}...")
            logger.info(f"   Chat ID: {self.emailer.chat_id}")
            
            # 1. 抓取資料
            logger.info("步驟 1/5: 抓取三大法人資料...")
            market_data = self.fetcher.fetch_market_data()
            stock_data = self.fetcher.fetch_stock_data(self.watch_list)
            
            if not market_data and not stock_data:
                logger.warning("無法取得資料，可能是假日或資料尚未更新")
                self.emailer.send_error_notification(
                    "無法取得三大法人數據",
                    "可能是假日或資料尚未更新，請稍後再試"
                )
                return
            
            # 2. 載入歷史資料
            logger.info("步驟 2/5: 載入歷史資料...")
            history = self.storage.load_history()
            
            # 3. 分析資料
            logger.info("步驟 3/5: 分析資料...")
            analysis = self.analyzer.analyze(market_data, stock_data, history)
            
            # 4. 儲存資料
            logger.info("步驟 4/5: 儲存資料...")
            self.storage.save_data(market_data, stock_data)
            
            # 5. 發送報告
            logger.info("步驟 5/5: 發送報告...")
            self.emailer.send_report(
                market_data=market_data,
                stock_data=stock_data,
                analysis=analysis,
                version=self.version
            )
            
            logger.info("="*60)
            logger.info("執行完成！")
            logger.info("="*60)
            
        except ValueError as e:
            # 設定錯誤
            logger.error(f"設定錯誤: {str(e)}")
            raise
            
        except Exception as e:
            logger.error(f"執行過程發生錯誤: {str(e)}", exc_info=True)
            try:
                self.emailer.send_error_notification(
                    "系統執行錯誤",
                    f"錯誤訊息: {str(e)}"
                )
            except:
                logger.error("無法發送錯誤通知")
            raise


def main():
    """主函數"""
    monitor = StockMonitor()
    monitor.run()


if __name__ == "__main__":
    main()
