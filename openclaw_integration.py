#!/usr/bin/env python3
"""
OpenClaw統合
OpenClawのツールを呼び出すためのヘルパー
"""

import subprocess
import json
import sys
import os
from typing import Optional
from dotenv import load_dotenv

# 環境変数の読み込み
load_dotenv()


def send_imessage(message: str, recipient: Optional[str] = None) -> bool:
    """
    iMessage経由で通知を送信（AppleScript使用）
    
    Args:
        message: 送信するメッセージ
        recipient: 受信者の名前（連絡先に登録されている名前）
    
    Returns:
        成功したかどうか
    """
    import subprocess
    
    # 受信者をデフォルト値 or 環境変数から取得
    if recipient is None:
        recipient = os.getenv('IMESSAGE_RECIPIENT', '受信者名')
    
    # メッセージとrecipientをサニタイズ（AppleScriptインジェクション対策）
    def sanitize_applescript(text):
        """AppleScript文字列をエスケープ"""
        return text.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n').replace('\r', '\\r')
    
    recipient_safe = sanitize_applescript(recipient)
    message_safe = sanitize_applescript(message)
    
    # AppleScript でメッセージ送信
    apple_script = f'''
    tell application "Messages"
        set targetBuddy to "{recipient_safe}"
        set targetService to 1st account whose service type = iMessage
        set textMessage to "{message_safe}"
        send textMessage to participant targetBuddy of targetService
    end tell
    '''
    
    try:
        subprocess.run(['osascript', '-e', apple_script], check=True, capture_output=True, text=True)
        print(f"✅ iMessage sent to {recipient}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"⚠️ Failed to send iMessage: {e.stderr}")
        return False
    except Exception as e:
        print(f"⚠️ Failed to send iMessage: {e}")
        return False


def send_chatwork_notification(
    message: str,
    api_token: Optional[str] = None,
    room_id: Optional[str] = None
) -> bool:
    """
    Chatworkに通知を送信
    
    Args:
        message: 送信するメッセージ
        api_token: Chatwork APIトークン（環境変数から取得も可能）
        room_id: Chatwork ルームID（環境変数から取得も可能）
    
    Returns:
        成功したかどうか
    """
    import os
    import requests
    
    api_token = api_token or os.getenv('CHATWORK_API_TOKEN')
    room_id = room_id or os.getenv('CHATWORK_ROOM_ID')
    
    if not api_token:
        print("⚠️ CHATWORK_API_TOKEN not set")
        return False
    
    try:
        url = f"https://api.chatwork.com/v2/rooms/{room_id}/messages"
        headers = {'X-ChatWorkToken': api_token}
        data = {'body': message}
        
        response = requests.post(url, headers=headers, data=data)
        response.raise_for_status()
        
        print(f"✅ Chatwork notification sent to room {room_id}")
        return True
    except Exception as e:
        print(f"⚠️ Failed to send Chatwork notification: {e}")
        return False


def notify_calendar_event(
    account: str,
    title: str,
    start_time: str,
    end_time: str,
    event_link: Optional[str] = None,
    channels: list = None,
    imessage_recipient: Optional[str] = None
) -> dict:
    """
    カレンダーイベント登録の通知を複数チャンネルに送信
    
    Args:
        account: 'crosslink' or 'programming_school'
        title: イベントのタイトル
        start_time: 開始時刻（ISO 8601形式）
        end_time: 終了時刻（ISO 8601形式）
        event_link: イベントのリンク（オプション）
        channels: 通知先チャンネル（['imessage', 'chatwork']）
        imessage_recipient: iMessageの送信先（連絡先の名前）
    
    Returns:
        各チャンネルの送信結果
    """
    from datetime import datetime
    
    if channels is None:
        channels = ['imessage', 'chatwork']
    
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
    message += f"タイトル: {title}\n"
    message += f"アカウント: {account_name_ja}\n"
    
    if event_link:
        message += f"リンク: {event_link}\n"
    
    # 各チャンネルに送信
    results = {}
    
    if 'imessage' in channels:
        results['imessage'] = send_imessage(message, imessage_recipient)
    
    if 'chatwork' in channels:
        results['chatwork'] = send_chatwork_notification(message)
    
    return results


# CLI エントリーポイント
if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python openclaw_integration.py <command> [args...]")
        print("Commands:")
        print("  imessage <message> [recipient]")
        print("  chatwork <message>")
        print("  notify <account> <title> <start> <end> [link]")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == 'imessage':
        if len(sys.argv) < 3:
            print("Usage: imessage <message> [recipient]")
            sys.exit(1)
        message = sys.argv[2]
        recipient = sys.argv[3] if len(sys.argv) > 3 else "さち"
        send_imessage(message, recipient)
    
    elif command == 'chatwork':
        message = ' '.join(sys.argv[2:])
        send_chatwork_notification(message)
    
    elif command == 'notify':
        account = sys.argv[2]
        title = sys.argv[3]
        start = sys.argv[4]
        end = sys.argv[5]
        link = sys.argv[6] if len(sys.argv) > 6 else None
        
        results = notify_calendar_event(account, title, start, end, link)
        print(json.dumps(results, indent=2))
    
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)
