#!/usr/bin/env python3
"""
カレンダーツール
OpenClaw が自然言語でカレンダー操作するための高レベル関数
"""

import sys
import os
from datetime import datetime, timedelta
import re
from typing import Optional, Dict, Any, List, Tuple

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from openclaw_helper import create_event, list_events, create_task, determine_account
from openclaw_integration import notify_calendar_event


def parse_datetime(text: str, base_date: Optional[datetime] = None) -> Optional[str]:
    """
    自然言語の日時表現を ISO 8601 形式に変換
    
    Args:
        text: '明日14時', '来週水曜 10:00', '3/5 15:00' など
        base_date: 基準日時（デフォルト: 現在）
    
    Returns:
        ISO 8601形式の日時文字列（例: '2026-03-05T14:00:00+09:00'）
    
    Examples:
        >>> parse_datetime('明日14時')
        '2026-03-05T14:00:00+09:00'
        >>> parse_datetime('来週水曜 10:00')
        '2026-03-11T10:00:00+09:00'
    """
    if base_date is None:
        base_date = datetime.now()
    
    # 相対的な日付
    if '明日' in text:
        target_date = base_date + timedelta(days=1)
    elif '今日' in text:
        target_date = base_date
    elif '来週' in text:
        target_date = base_date + timedelta(days=7)
        # 曜日指定があれば調整
        if '月' in text or '月曜' in text:
            target_date += timedelta(days=(0 - target_date.weekday()) % 7)
        elif '火' in text or '火曜' in text:
            target_date += timedelta(days=(1 - target_date.weekday()) % 7)
        elif '水' in text or '水曜' in text:
            target_date += timedelta(days=(2 - target_date.weekday()) % 7)
        elif '木' in text or '木曜' in text:
            target_date += timedelta(days=(3 - target_date.weekday()) % 7)
        elif '金' in text or '金曜' in text:
            target_date += timedelta(days=(4 - target_date.weekday()) % 7)
    else:
        # 絶対的な日付（例: 3/5, 2026-03-05）
        date_match = re.search(r'(\d{1,2})/(\d{1,2})', text)
        if date_match:
            month = int(date_match.group(1))
            day = int(date_match.group(2))
            year = base_date.year
            if month < base_date.month:
                year += 1
            target_date = datetime(year, month, day)
        else:
            target_date = base_date
    
    # 時刻の抽出
    time_match = re.search(r'(\d{1,2})[:時](\d{1,2})?', text)
    if time_match:
        hour = int(time_match.group(1))
        minute = int(time_match.group(2)) if time_match.group(2) else 0
        target_date = target_date.replace(hour=hour, minute=minute, second=0, microsecond=0)
    
    # ISO 8601 形式に変換
    return target_date.strftime('%Y-%m-%dT%H:%M:%S+09:00')


def add_calendar_event_from_text(text: str) -> Dict[str, Any]:
    """
    自然言語からカレンダーイベントを作成
    
    Args:
        text: '明日14時にA社と打ち合わせ、1時間' など
    
    Returns:
        作成されたイベントの情報
    
    Examples:
        >>> add_calendar_event_from_text('明日14時にA社と打ち合わせ、1時間')
        >>> add_calendar_event_from_text('来週水曜10時からプロシーズ定例会、90分')
    """
    # アカウント判定
    account, is_explicit = determine_account(text)
    
    # 開始時刻の抽出
    start_time = parse_datetime(text)
    if not start_time:
        raise ValueError("開始時刻が見つかりません")
    
    # 終了時刻の推定
    duration_match = re.search(r'(\d+)\s*(時間|分|h|min)', text)
    if duration_match:
        duration = int(duration_match.group(1))
        unit = duration_match.group(2)
        
        if unit in ['時間', 'h']:
            end_dt = datetime.fromisoformat(start_time.replace('+09:00', '')) + timedelta(hours=duration)
        else:  # 分
            end_dt = datetime.fromisoformat(start_time.replace('+09:00', '')) + timedelta(minutes=duration)
        
        end_time = end_dt.strftime('%Y-%m-%dT%H:%M:%S+09:00')
    else:
        # デフォルト: 1時間
        end_dt = datetime.fromisoformat(start_time.replace('+09:00', '')) + timedelta(hours=1)
        end_time = end_dt.strftime('%Y-%m-%dT%H:%M:%S+09:00')
    
    # タイトルの抽出（簡易版）
    title = text.split('、')[0].split('。')[0]
    # 時刻表現を削除
    title = re.sub(r'\d+[:時]\d*', '', title)
    title = re.sub(r'(明日|今日|来週|月曜|火曜|水曜|木曜|金曜|土曜|日曜)', '', title)
    title = re.sub(r'(\d+)\s*(時間|分)', '', title)
    title = title.strip()
    
    # アカウント名の日本語化
    account_name_ja = {
        'crosslink': 'クロスリンク',
        'programming_school': 'プログラミングスクール'
    }.get(account, account)
    
    # 明示的な指定がない場合は確認が必要
    if not is_explicit:
        return {
            'needs_confirmation': True,
            'account': account,
            'account_name': account_name_ja,
            'title': title,
            'start_time': start_time,
            'end_time': end_time,
            'summary': f"🔔 確認\n\n"
                      f"「{title}」を\n"
                      f"【{account_name_ja}】のカレンダーに登録しますか？\n\n"
                      f"日時: {start_time} - {end_time}\n\n"
                      f"OKなら「はい」または「登録して」と返信してください。"
        }
    
    # 明示的な指定がある場合は即登録
    event = create_event(
        account=account,
        title=title,
        start=start_time,
        end=end_time
    )
    
    # 通知送信（LINE + Chatwork）
    notify_calendar_event(
        account=account,
        title=title,
        start_time=start_time,
        end_time=end_time,
        event_link=event.get('htmlLink')
    )
    
    return {
        'needs_confirmation': False,
        'account': account,
        'event': event,
        'summary': f"✅ {account_name_ja} のカレンダーに登録しました\n"
                  f"日時: {start_time} - {end_time}\n"
                  f"タイトル: {title}\n"
                  f"リンク: {event.get('htmlLink')}"
    }


def confirm_and_create_event(
    account: str,
    title: str,
    start_time: str,
    end_time: str
) -> Dict[str, Any]:
    """
    確認後にカレンダーイベントを作成
    
    Args:
        account: 'crosslink' or 'programming_school'
        title: イベントのタイトル
        start_time: 開始時刻（ISO 8601形式）
        end_time: 終了時刻（ISO 8601形式）
    
    Returns:
        作成されたイベントの情報
    """
    # イベント作成
    event = create_event(
        account=account,
        title=title,
        start=start_time,
        end=end_time
    )
    
    # 通知送信
    notify_calendar_event(
        account=account,
        title=title,
        start_time=start_time,
        end_time=end_time,
        event_link=event.get('htmlLink')
    )
    
    # アカウント名の日本語化
    account_name_ja = {
        'crosslink': 'クロスリンク',
        'programming_school': 'プログラミングスクール'
    }.get(account, account)
    
    return {
        'account': account,
        'event': event,
        'summary': f"✅ {account_name_ja} のカレンダーに登録しました\n"
                  f"日時: {start_time} - {end_time}\n"
                  f"タイトル: {title}\n"
                  f"リンク: {event.get('htmlLink')}"
    }


def get_upcoming_events(account: Optional[str] = None, days: int = 7) -> str:
    """
    今後の予定を取得して整形
    
    Args:
        account: 'crosslink', 'programming_school', または None（両方）
        days: 何日先まで取得するか
    
    Returns:
        整形されたイベント一覧
    
    Examples:
        >>> print(get_upcoming_events('crosslink', days=3))
        >>> print(get_upcoming_events(days=1))  # 両アカウント
    """
    accounts = [account] if account else ['crosslink', 'programming_school']
    
    result = "📅 今後の予定\n\n"
    
    for acc in accounts:
        account_name = 'クロスリンク' if acc == 'crosslink' else 'プログラミングスクール'
        result += f"【{account_name}】\n"
        
        try:
            events = list_events(acc, days_ahead=days)
            
            if not events:
                result += "  予定なし\n\n"
                continue
            
            for event in events[:10]:  # 最大10件
                start = event['start'].get('dateTime', event['start'].get('date'))
                title = event['summary']
                
                # 日時フォーマット
                try:
                    dt = datetime.fromisoformat(start.replace('Z', '+00:00'))
                    time_str = dt.strftime('%m/%d(%a) %H:%M')
                except:
                    time_str = start
                
                result += f"  - {time_str}: {title}\n"
            
            result += "\n"
        
        except Exception as e:
            result += f"  ⚠️ エラー: {e}\n\n"
    
    return result


# CLI エントリーポイント
if __name__ == '__main__':
    import json
    
    if len(sys.argv) < 2:
        print("Usage: python calendar_tools.py <command> [args...]")
        print("Commands:")
        print("  add <text>          - 自然言語でイベント作成")
        print("  list [account] [days] - 予定一覧")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == 'add':
        text = ' '.join(sys.argv[2:])
        result = add_calendar_event_from_text(text)
        print(result['summary'])
    
    elif command == 'list':
        account = sys.argv[2] if len(sys.argv) > 2 and sys.argv[2] in ['crosslink', 'programming_school'] else None
        days = int(sys.argv[3]) if len(sys.argv) > 3 else 7
        print(get_upcoming_events(account, days))
    
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)
