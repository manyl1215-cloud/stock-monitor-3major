#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Telegram 通知模組 - 發送分析報告到 Telegram
"""

import os
import requests
import logging
from datetime import datetime
from typing import Dict, Optional

logger = logging.getLogger(__name__)


class TelegramNotifier:
    """Telegram 通知器"""
    
    def __init__(self):
        # 從環境變數讀取 Telegram 設定
        self.bot_token = os.getenv('TELEGRAM_BOT_TOKEN', '')
        self.chat_id = os.getenv('TELEGRAM_CHAT_ID', '')
        
        if not self.bot_token or not self.chat_id:
            logger.warning("Telegram 設定未完成，通知功能將無法使用")
        else:
            logger.info(f"Telegram Bot 已初始化 (Chat ID: {self.chat_id})")
    
    def send_report(self, market_data: Dict, stock_data: Dict, 
                   analysis: Dict, version: str):
        """發送每日分析報告"""
        
        if not self.bot_token or not self.chat_id:
            logger.error("Telegram 設定不完整，無法發送通知")
            return
        
        # 產生報告文字
        message = self._generate_report_text(market_data, stock_data, analysis, version)
        
        # 發送訊息
        self._send_message(message)
    
    def send_error_notification(self, error_title: str, error_message: str):
        """發送錯誤通知"""
        
        if not self.bot_token or not self.chat_id:
            logger.error("Telegram 設定不完整，無法發送錯誤通知")
            return
        
        message = f"""
⚠️ *系統執行錯誤*

🕐 *錯誤時間：*
{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

❌ *錯誤類型：*
{error_title}

📝 *錯誤訊息：*
```
{error_message}
```

請檢查系統設定或查看執行記錄。
"""
        
        self._send_message(message)
    
    def _send_message(self, message: str, parse_mode: str = 'Markdown'):
        """發送 Telegram 訊息"""
        
        url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
        
        payload = {
            'chat_id': self.chat_id,
            'text': message,
            'parse_mode': parse_mode,
            'disable_web_page_preview': True
        }
        
        try:
            response = requests.post(url, json=payload, timeout=30)
            response.raise_for_status()
            
            logger.info(f"✅ Telegram 訊息已發送至 Chat ID: {self.chat_id}")
            
        except Exception as e:
            logger.error(f"發送 Telegram 訊息失敗: {str(e)}")
            raise
    
    def _generate_report_text(self, market_data: Dict, stock_data: Dict, 
                             analysis: Dict, version: str) -> str:
        """產生報告文字（Markdown 格式）"""
        
        # 標題
        today = datetime.now().strftime('%Y/%m/%d')
        message = f"""
📊 *三大法人買賣監測報告*

📅 *報告日期：* {today}
🕐 *產生時間：* {datetime.now().strftime('%H:%M:%S')}
💻 *系統版本：* {version}

━━━━━━━━━━━━━━━━━━━━
"""
        
        # 大盤分析
        if analysis.get('market'):
            message += self._generate_market_section(analysis['market'])
        
        # 個股分析
        if analysis.get('stocks'):
            message += self._generate_stock_section(analysis['stocks'])
        
        # 頁尾
        message += f"""
━━━━━━━━━━━━━━━━━━━━
📌 *資料來源：* 台灣證券交易所
⏰ *更新時間：* {datetime.now().strftime('%H:%M:%S')}
"""
        
        return message
    
    def _generate_market_section(self, market_analysis: Dict) -> str:
        """產生大盤分析區塊"""
        
        today = market_analysis['today']
        
        text = """
🏛️ *大盤三大法人*

📈 *今日買賣金額（億元）*
"""
        
        # 今日買賣摘要
        for name, key in [('外資', 'foreign'), ('投信', 'trust'), 
                         ('自營商', 'dealer'), ('合計', 'total')]:
            value = today[key]
            emoji = '🟢' if value > 0 else '🔴'
            status = '買超' if value > 0 else '賣超'
            
            if key == 'total':
                text += f"\n*{emoji} {name}:* `{value:+.2f}` 億 ({status})"
            else:
                text += f"\n{emoji} {name}: `{value:+.2f}` 億 ({status})"
        
        # 警示訊息
        if market_analysis.get('alerts'):
            text += "\n\n⚠️ *大額交易警示*\n"
            for alert in market_analysis['alerts']:
                text += f"🔴 {alert['message']}\n"
        
        # 趨勢分析
        text += "\n\n📊 *連續買賣趨勢*\n"
        
        for trend in market_analysis['trends'].values():
            if trend['consecutive'] >= 3:
                emoji = '🟢' if trend['direction'] == 'buy' else '🔴'
                direction = '連買' if trend['direction'] == 'buy' else '連賣'
                
                text += f"{emoji} {trend['name']}: *{trend['consecutive']}天{direction}* "
                text += f"(累計 `{trend['total_amount']:+.2f}` 億)\n"
        
        return text
    
    def _generate_stock_section(self, stock_analysis: Dict) -> str:
        """產生個股分析區塊"""
        
        text = "\n━━━━━━━━━━━━━━━━━━━━\n"
        text += "📈 *個股三大法人*\n"
        
        # 超大額交易
        if stock_analysis.get('large_trades_super'):
            text += "\n🔥 *超大額交易（≥1.5億）*\n"
            
            for stock in stock_analysis['large_trades_super'][:5]:
                emoji = '🟢' if stock['total'] > 0 else '🔴'
                text += f"\n{emoji} *{stock['code']} {stock['name']}*\n"
                text += f"   外資: `{stock['foreign']:+.0f}` | "
                text += f"投信: `{stock['trust']:+.0f}` | "
                text += f"自營: `{stock['dealer']:+.0f}`\n"
                text += f"   *合計: `{stock['total']:+.0f}` 張* "
                text += f"(~{stock['amount']:.2f}億)\n"
        
        # 大額交易
        elif stock_analysis.get('large_trades'):
            text += "\n💰 *大額交易（≥0.5億）*\n"
            
            for stock in stock_analysis['large_trades'][:8]:
                emoji = '🟢' if stock['total'] > 0 else '🔴'
                text += f"{emoji} {stock['code']} {stock['name']}: "
                text += f"`{stock['total']:+.0f}` 張\n"
        
        # 總是顯示前10大買賣超（除非大額交易已經很多了）
        num_large = len(stock_analysis.get('large_trades_super', [])) + len(stock_analysis.get('large_trades', []))
        
        if num_large < 10:  # 如果大額交易少於10筆，補充顯示買賣超排行
            # 前10大買超
            if stock_analysis.get('top_buys'):
                text += "\n🟢 *前10大買超*\n"
                
                for i, stock in enumerate(stock_analysis['top_buys'][:10], 1):
                    text += f"{i}. {stock['code']} {stock['name']}: "
                    text += f"`+{stock['total']:.0f}` 張\n"
                    text += f"   (外: `{stock['foreign']:+.0f}` | "
                    text += f"投: `{stock['trust']:+.0f}` | "
                    text += f"自: `{stock['dealer']:+.0f}`)\n"
            
            # 前10大賣超
            if stock_analysis.get('top_sells'):
                text += "\n🔴 *前10大賣超*\n"
                
                for i, stock in enumerate(stock_analysis['top_sells'][:10], 1):
                    text += f"{i}. {stock['code']} {stock['name']}: "
                    text += f"`{stock['total']:.0f}` 張\n"
                    text += f"   (外: `{stock['foreign']:+.0f}` | "
                    text += f"投: `{stock['trust']:+.0f}` | "
                    text += f"自: `{stock['dealer']:+.0f}`)\n"
        
        # 連續買超
        if stock_analysis.get('consecutive_buys'):
            text += "\n📊 *連續買超（≥3天）*\n"
            
            for stock in stock_analysis['consecutive_buys'][:5]:
                text += f"🟢 *{stock['code']} {stock['name']}*\n"
                text += f"   {stock['consecutive']['days']}天連買 | "
                text += f"累計 `+{stock['consecutive']['total_amount']:.0f}` 張\n"
        
        # 連續賣超
        if stock_analysis.get('consecutive_sells'):
            text += "\n📉 *連續賣超（≥3天）*\n"
            
            for stock in stock_analysis['consecutive_sells'][:5]:
                text += f"🔴 *{stock['code']} {stock['name']}*\n"
                text += f"   {stock['consecutive']['days']}天連賣 | "
                text += f"累計 `{stock['consecutive']['total_amount']:.0f}` 張\n"
        
        return text


# 保留舊的 EmailSender 類別以向後相容
EmailSender = TelegramNotifier


if __name__ == "__main__":
    # 測試
    logging.basicConfig(level=logging.INFO)
    
    notifier = TelegramNotifier()
    
    # 測試資料
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
                'foreign': 2500.0,
                'trust': 800.0,
                'dealer': 150.0,
                'total': 3450.0
            }
        ]
    }
    
    analysis = {
        'market': {
            'today': market_data,
            'alerts': [
                {'message': '外資大買 125.45 億元'}
            ],
            'trends': {
                'foreign': {
                    'name': '外資',
                    'consecutive': 5,
                    'direction': 'buy',
                    'total_amount': 456.78
                }
            }
        },
        'stocks': {
            'large_trades_super': [stock_data['stocks'][0]],
            'large_trades': [],
            'consecutive_buys': [],
            'consecutive_sells': []
        }
    }
    
    notifier.send_report(market_data, stock_data, analysis, 'v2.0.0-telegram')

    """Email 發送器"""
    
    def __init__(self):
        # 從環境變數讀取 SMTP 設定
        self.smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', '587'))
        self.smtp_user = os.getenv('SMTP_USER', '')
        self.smtp_password = os.getenv('SMTP_PASSWORD', '')
        self.from_email = os.getenv('FROM_EMAIL', self.smtp_user)
        
        if not self.smtp_user or not self.smtp_password:
            logger.warning("SMTP 帳號密碼未設定，Email 功能將無法使用")
    
    def send_report(self, to_email: str, market_data: Dict, 
                   stock_data: Dict, analysis: Dict, version: str):
        """發送每日分析報告"""
        subject = f"📊 三大法人監測報告 - {datetime.now().strftime('%Y/%m/%d')}"
        html_body = self._generate_report_html(market_data, stock_data, analysis, version)
        
        self._send_email(to_email, subject, html_body)
    
    def send_error_email(self, to_email: str, error_title: str, error_message: str):
        """發送錯誤通知"""
        subject = f"⚠️ 三大法人監測系統錯誤通知"
        html_body = f"""
        <html>
        <body style="font-family: 'Microsoft JhengHei', Arial, sans-serif;">
            <h2>系統執行錯誤</h2>
            <p><strong>錯誤時間：</strong>{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p><strong>錯誤類型：</strong>{error_title}</p>
            <div style="background: #ffe6e6; padding: 15px; border-left: 4px solid #e74c3c;">
                <strong>錯誤訊息：</strong><br>
                {error_message}
            </div>
            <p>請檢查系統設定或查看執行記錄。</p>
        </body>
        </html>
        """
        
        self._send_email(to_email, subject, html_body)
    
    def _send_email(self, to_email: str, subject: str, html_body: str):
        """發送 HTML Email"""
        if not self.smtp_user or not self.smtp_password:
            logger.error("SMTP 設定不完整，無法發送 Email")
            logger.info(f"Email 內容:\nTo: {to_email}\nSubject: {subject}")
            return
        
        try:
            # 建立郵件
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.from_email
            msg['To'] = to_email
            
            # 附加 HTML 內容
            html_part = MIMEText(html_body, 'html', 'utf-8')
            msg.attach(html_part)
            
            # 發送
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)
            
            logger.info(f"✅ Email 已發送至: {to_email}")
            
        except Exception as e:
            logger.error(f"發送 Email 失敗: {str(e)}")
            raise
    
    def _generate_report_html(self, market_data: Dict, stock_data: Dict, 
                             analysis: Dict, version: str) -> str:
        """產生 HTML 報告"""
        
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <style>
        body {{ 
            font-family: "Microsoft JhengHei", Arial, sans-serif; 
            line-height: 1.6;
            color: #333;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
        }}
        h1 {{ 
            color: #2c3e50; 
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
        }}
        h2 {{ 
            color: #34495e; 
            background: #ecf0f1;
            padding: 10px;
            border-left: 4px solid #3498db;
        }}
        .alert {{ 
            background: #ffe6e6; 
            padding: 15px; 
            border-left: 4px solid #e74c3c;
            margin: 10px 0;
        }}
        .warning {{
            background: #fff9e6;
            padding: 15px;
            border-left: 4px solid #f39c12;
            margin: 10px 0;
        }}
        .info {{ 
            background: #e8f4f8; 
            padding: 15px; 
            border-left: 4px solid #3498db;
            margin: 10px 0;
        }}
        table {{ 
            width: 100%; 
            border-collapse: collapse; 
            margin: 15px 0;
            background: white;
        }}
        th {{ 
            background: #34495e; 
            color: white; 
            padding: 12px;
            text-align: left;
        }}
        td {{ 
            padding: 10px; 
            border-bottom: 1px solid #ddd;
        }}
        tr:hover {{ background: #f5f5f5; }}
        .buy {{ color: #27ae60; font-weight: bold; }}
        .sell {{ color: #e74c3c; font-weight: bold; }}
        .positive {{ color: #27ae60; }}
        .negative {{ color: #e74c3c; }}
        .badge {{
            display: inline-block;
            padding: 3px 8px;
            border-radius: 3px;
            font-size: 0.9em;
            font-weight: bold;
        }}
        .badge-danger {{ background: #e74c3c; color: white; }}
        .badge-warning {{ background: #f39c12; color: white; }}
        .badge-success {{ background: #27ae60; color: white; }}
    </style>
</head>
<body>
    <h1>📊 三大法人買賣監測報告</h1>
    <p><strong>報告日期：</strong>{datetime.now().strftime('%Y/%m/%d')}</p>
    <p><strong>產生時間：</strong>{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    <p style="color: #7f8c8d; font-size: 0.85em;"><strong>系統版本：</strong>{version}</p>
"""
        
        # 大盤分析
        if analysis.get('market'):
            html += self._generate_market_section(analysis['market'])
        
        # 個股分析
        if analysis.get('stocks'):
            html += self._generate_stock_section(analysis['stocks'])
        
        # 頁尾
        html += f"""
    <hr>
    <p style="color: #7f8c8d; font-size: 0.9em;">
        <strong>三大法人買賣監測系統 (Python)</strong> {version}<br>
        Taiwan Stock Institutional Investors Monitor<br>
        <br>
        此報告由 Python 自動產生<br>
        資料來源：台灣證券交易所<br>
        GitHub: https://github.com/your-repo/stock-monitor<br>
        <br>
        更新時間：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    </p>
</body>
</html>
"""
        
        return html
    
    def _generate_market_section(self, market_analysis: Dict) -> str:
        """產生大盤分析區塊"""
        today = market_analysis['today']
        
        html = '<h2>🏛️ 大盤三大法人</h2>'
        
        # 今日買賣摘要
        html += '<div class="info">'
        html += '<h3>今日買賣金額（億元）</h3>'
        html += '<table>'
        html += '<tr><th>法人</th><th>買賣金額</th><th>狀態</th></tr>'
        
        for name, key in [('外資', 'foreign'), ('投信', 'trust'), ('自營商', 'dealer'), ('合計', 'total')]:
            value = today[key]
            color_class = 'positive' if value >= 0 else 'negative'
            status = '<span class="buy">買超</span>' if value > 0 else '<span class="sell">賣超</span>'
            style = 'font-weight: bold; background: #ecf0f1;' if key == 'total' else ''
            
            html += f"""
            <tr style="{style}">
                <td>{name}</td>
                <td class="{color_class}">{'+'if value > 0 else ''}{value:.2f}</td>
                <td>{status}</td>
            </tr>
            """
        
        html += '</table></div>'
        
        # 警示訊息
        if market_analysis.get('alerts'):
            html += '<div class="alert"><h3>⚠️ 大額交易警示</h3>'
            for alert in market_analysis['alerts']:
                html += f"<p>🔴 {alert['message']}</p>"
            html += '</div>'
        
        # 趨勢分析
        html += '<div class="warning"><h3>📈 連續買賣趨勢</h3><table>'
        html += '<tr><th>法人</th><th>連續天數</th><th>方向</th><th>累計金額（億）</th></tr>'
        
        for trend in market_analysis['trends'].values():
            if trend['consecutive'] >= 3:
                badge_class = 'badge-danger' if trend['consecutive'] >= 5 else 'badge-warning'
                direction = '<span class="buy">連買</span>' if trend['direction'] == 'buy' else '<span class="sell">連賣</span>'
                color_class = 'positive' if trend['total_amount'] >= 0 else 'negative'
                
                html += f"""
                <tr>
                    <td>{trend['name']}</td>
                    <td><span class="badge {badge_class}">{trend['consecutive']} 天</span></td>
                    <td>{direction}</td>
                    <td class="{color_class}">{'+'if trend['total_amount'] > 0 else ''}{trend['total_amount']:.2f}</td>
                </tr>
                """
        
        html += '</table></div>'
        
        return html
    
    def _generate_stock_section(self, stock_analysis: Dict) -> str:
        """產生個股分析區塊"""
        html = '<h2>📈 個股三大法人</h2>'
        
        # 超大額交易
        if stock_analysis.get('large_trades_super'):
            html += '<div class="alert"><h3>🔥 超大額交易警示（≥1.5億）</h3><table>'
            html += '<tr><th>股票</th><th>外資</th><th>投信</th><th>自營商</th><th>合計（張）</th><th>估算金額</th></tr>'
            
            for stock in stock_analysis['large_trades_super'][:10]:
                html += f"""
                <tr>
                    <td><strong>{stock['code']} {stock['name']}</strong></td>
                    <td class="{'positive' if stock['foreign'] >= 0 else 'negative'}">{'+'if stock['foreign'] > 0 else ''}{stock['foreign']:.0f}</td>
                    <td class="{'positive' if stock['trust'] >= 0 else 'negative'}">{'+'if stock['trust'] > 0 else ''}{stock['trust']:.0f}</td>
                    <td class="{'positive' if stock['dealer'] >= 0 else 'negative'}">{'+'if stock['dealer'] > 0 else ''}{stock['dealer']:.0f}</td>
                    <td class="{'buy' if stock['total'] >= 0 else 'sell'}">{'+'if stock['total'] > 0 else ''}{stock['total']:.0f}</td>
                    <td>~{stock['amount']:.2f}億</td>
                </tr>
                """
            
            html += '</table></div>'
        
        # 連續買超
        if stock_analysis.get('consecutive_buys'):
            html += '<div class="info"><h3>📊 連續買超（≥3天）</h3><table>'
            html += '<tr><th>股票</th><th>連續天數</th><th>累計（張）</th><th>今日（張）</th></tr>'
            
            for stock in stock_analysis['consecutive_buys'][:10]:
                html += f"""
                <tr>
                    <td>{stock['code']} {stock['name']}</td>
                    <td><span class="badge badge-success">{stock['consecutive']['days']} 天</span></td>
                    <td class="buy">+{stock['consecutive']['total_amount']:.0f}</td>
                    <td class="buy">+{stock['total']:.0f}</td>
                </tr>
                """
            
            html += '</table></div>'
        
        return html


if __name__ == "__main__":
    # 測試
    logging.basicConfig(level=logging.INFO)
    emailer = EmailSender()
    
    # 測試資料
    market_data = {'date': '115/04/21', 'foreign': 125.45, 'trust': -23.18, 'dealer': 8.92, 'total': 111.19}
    stock_data = {'date': '1150421', 'stocks': []}
    analysis = {'market': {'today': market_data, 'alerts': [], 'trends': {}}, 'stocks': None}
    
    emailer.send_report('test@example.com', market_data, stock_data, analysis, 'v2.0.0-test')
