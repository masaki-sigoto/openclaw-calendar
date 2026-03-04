#!/usr/bin/env python3
"""
通知サービス
カレンダー登録時にLINE/Chatworkに通知を送信
"""

import os
import requests
from typing import Optional, Dict, Any
from datetime import datetime


class NotificationService:
    """通知送信サービス"""
    
    def __init__(self):
        self.line_enabled = False
        self.chatwork_enabled = False
        self.chatwork_api_token = os.getenv('CHATWORK_API_TOKEN')
        self.chatwork_room_id = os.getenv('CHATWORK_ROOM_ID')
        
        # Chatwork API トークンがあれば有効化
        if self.chatwork_api_token:
            self.chatwork_enabled = True
    
    def send_calendar_notification(
        self,
        account: str,
        summary: str,
        start_time: str,
        end_time: str,
        description: Optional[str] = None,
        location: Optional[str] = None,
        event_link: Optional[str] = None
    ):
        """
        カレンダー登録時の通知を送信
        
        Args:
            account: アカウント名（crosslink / programming_school）
            summary: イベントのタイトル
            start_time: 開始時刻（ISO 8601形式）
            end_time: 終了時刻
            description: 説明（オプション）
            location: 場所（オプション）
            event_link: イベントのリンク（オプション）
        """
        # アカウント名の日本語化
        account_name_ja = {
            'crosslink': 'クロスリンク',
            'programming_school': 'プログラミングスクール'
        }.get(account, account)
        
        # 時刻のフォーマット
        try:
            start_dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
            end_dt = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
            time_str = f"{start_dt.strftime('%Y/%m/%d(%a) %H:%M')}-{end_dt.strftime('%H:%M')}"
        except:
            time_str = f"{start_time} - {end_time}"
        
        # 通知メッセージ作成
        message = f"📅 予定を登録しました\n\n"
        message += f"日時: {time_str}\n"
        message += f"タイトル: {summary}\n"
        message += f"アカウント: {account_name_ja}\n"
        
        if location:
            message += f"場所: {location}\n"
        if description:
            message += f"説明: {description}\n"
        if event_link:
            message += f"リンク: {event_link}\n"
        
        # Chatworkに送信
        if self.chatwork_enabled:
            self._send_chatwork(message)
        
        # LINEに送信（TODO: 実装）
        if self.line_enabled:
            self._send_line(message)
    
    def _send_chatwork(self, message: str):
        """Chatworkにメッセージ送信"""
        try:
            url = f"https://api.chatwork.com/v2/rooms/{self.chatwork_room_id}/messages"
            headers = {
                'X-ChatWorkToken': self.chatwork_api_token
            }
            data = {
                'body': message
            }
            response = requests.post(url, headers=headers, data=data)
            response.raise_for_status()
            print(f"✅ Chatwork notification sent to room {self.chatwork_room_id}")
        except Exception as e:
            print(f"⚠️ Failed to send Chatwork notification: {e}")
    
    def _send_line(self, message: str):
        """LINEにメッセージ送信（OpenClaw経由）"""
        try:
            # OpenClaw の message ツールを使う場合
            # ここではファイルに書き出して、OpenClawに処理させる
            notification_file = '/tmp/openclaw_calendar_notification.txt'
            with open(notification_file, 'w', encoding='utf-8') as f:
                f.write(message)
            print(f"✅ LINE notification prepared: {notification_file}")
            # OpenClaw側で読み取って送信
        except Exception as e:
            print(f"⚠️ Failed to prepare LINE notification: {e}")
