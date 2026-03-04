#!/usr/bin/env python3
"""
リマインダー機能
予定の事前通知
"""

import sys
import os
from datetime import datetime, timedelta
from typing import List, Dict, Any

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from calendar_view import get_unified_calendar
from openclaw_integration import send_imessage, send_chatwork_notification


def check_upcoming_events(minutes_ahead: int = 60) -> List[Dict[str, Any]]:
    """
    もうすぐ始まる予定をチェック
    
    Args:
        minutes_ahead: 何分後の予定までチェックするか
    
    Returns:
        もうすぐ始まる予定のリスト
    """
    # 今後の予定を取得
    all_events = get_unified_calendar(days_ahead=1)
    
    now = datetime.now()
    threshold = now + timedelta(minutes=minutes_ahead)
    
    upcoming = []
    for event in all_events:
        try:
            # 開始時刻をパース
            start_str = event['start']
            if 'T' in start_str:
                start_dt = datetime.fromisoformat(start_str.replace('Z', '+00:00'))
                
                # タイムゾーンを削除して比較
                start_dt = start_dt.replace(tzinfo=None)
                
                # もうすぐ始まる予定かどうか
                if now <= start_dt <= threshold:
                    minutes_until = int((start_dt - now).total_seconds() / 60)
                    event['minutes_until'] = minutes_until
                    upcoming.append(event)
        except Exception as e:
            print(f"⚠️ Failed to parse event: {e}")
    
    return upcoming


def send_reminder(event: Dict[str, Any], minutes_before: int = 60):
    """
    リマインダーを送信
    
    Args:
        event: イベント情報
        minutes_before: 何分前に通知するか
    """
    # メッセージを作成
    minutes_until = event.get('minutes_until', minutes_before)
    
    message = f"🔔 リマインダー\n\n"
    message += f"**{event['title']}** が{minutes_until}分後に始まります\n\n"
    message += f"日時: {event['start']}\n"
    message += f"アカウント: {event['account_name']}\n"
    
    if event.get('location'):
        message += f"場所: {event['location']}\n"
    
    if event.get('link'):
        message += f"リンク: {event['link']}\n"
    
    # 通知送信
    send_imessage(message)
    send_chatwork_notification(message)


def run_reminder_check(minutes_ahead: int = 60):
    """
    リマインダーチェックを実行
    
    Args:
        minutes_ahead: 何分後の予定までチェックするか
    """
    print(f"📅 リマインダーチェック開始（{minutes_ahead}分後まで）")
    
    upcoming = check_upcoming_events(minutes_ahead=minutes_ahead)
    
    if not upcoming:
        print("✅ もうすぐ始まる予定はありません")
        return
    
    print(f"🔔 {len(upcoming)}件の予定がもうすぐ始まります\n")
    
    for event in upcoming:
        print(f"  - {event['title']} ({event['minutes_until']}分後)")
        send_reminder(event, minutes_before=event['minutes_until'])
    
    print("\n✅ リマインダー送信完了")


def get_daily_summary() -> str:
    """
    今日の予定サマリーを取得
    
    Returns:
        サマリーテキスト
    """
    # 今日の予定を取得
    all_events = get_unified_calendar(days_ahead=1)
    
    now = datetime.now()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    today_end = now.replace(hour=23, minute=59, second=59, microsecond=999999)
    
    today_events = []
    for event in all_events:
        try:
            start_str = event['start']
            if 'T' in start_str:
                start_dt = datetime.fromisoformat(start_str.replace('Z', '+00:00')).replace(tzinfo=None)
                
                if today_start <= start_dt <= today_end:
                    today_events.append(event)
            else:
                # 終日イベント
                today_events.append(event)
        except:
            pass
    
    if not today_events:
        return "📅 今日の予定はありません"
    
    # サマリーを作成
    summary = f"📅 **今日の予定（{len(today_events)}件）**\n\n"
    
    for event in today_events:
        start = event['start']
        try:
            if 'T' in start:
                dt = datetime.fromisoformat(start.replace('Z', '+00:00'))
                time_str = dt.strftime('%H:%M')
            else:
                time_str = '終日'
        except:
            time_str = '?'
        
        summary += f"**{time_str}** - {event['title']}\n"
        summary += f"  ({event['account_name']})\n"
        
        if event.get('location'):
            summary += f"  📍 {event['location']}\n"
        
        summary += "\n"
    
    return summary


def send_daily_summary():
    """今日の予定サマリーを送信"""
    summary = get_daily_summary()
    
    # 通知送信
    send_imessage(summary)
    send_chatwork_notification(summary)
    
    print(summary)
    print("\n✅ 今日の予定サマリーを送信しました")


# CLI エントリーポイント
if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python calendar_reminder.py <command> [args...]")
        print("Commands:")
        print("  check [minutes]  - もうすぐ始まる予定をチェック（デフォルト: 60分）")
        print("  daily            - 今日の予定サマリーを送信")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == 'check':
        minutes = int(sys.argv[2]) if len(sys.argv) > 2 else 60
        run_reminder_check(minutes_ahead=minutes)
    
    elif command == 'daily':
        send_daily_summary()
    
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)
