#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
本地排程執行腳本
使用 schedule 套件定時執行監測任務
"""

import schedule
import time
import logging
from datetime import datetime
from main import StockMonitor

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def job():
    """排程任務"""
    logger.info("=" * 60)
    logger.info(f"開始執行排程任務 - {datetime.now()}")
    logger.info("=" * 60)
    
    try:
        monitor = StockMonitor()
        monitor.run()
    except Exception as e:
        logger.error(f"執行失敗: {str(e)}", exc_info=True)


def main():
    """主程式"""
    logger.info("🚀 三大法人監測系統 - 排程服務已啟動")
    logger.info("每天晚上 18:00 (台灣時間) 執行")
    logger.info("按 Ctrl+C 停止服務")
    logger.info("-" * 60)
    
    # 設定排程：每天晚上 6 點執行
    schedule.every().day.at("18:00").do(job)
    
    # 也可以設定其他排程，例如：
    # schedule.every().day.at("09:00").do(job)  # 每天早上 9 點
    # schedule.every().hour.do(job)  # 每小時
    # schedule.every(30).minutes.do(job)  # 每 30 分鐘
    
    # 顯示下次執行時間
    next_run = schedule.next_run()
    logger.info(f"下次執行時間: {next_run}")
    
    # 持續運行
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)  # 每分鐘檢查一次
    except KeyboardInterrupt:
        logger.info("\n停止排程服務")


if __name__ == "__main__":
    main()
