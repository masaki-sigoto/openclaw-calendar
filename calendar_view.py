#!/usr/bin/env python3
"""
統合カレンダー表示
複数アカウントの予定を統合して表示
"""

import sys
import os
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from openclaw_helper import list_events, get_mcp


def get_unified_calendar(days_ahead: int = 7, start_date: Optional[datetime] = None) -> List[Dict[str, Any]]:
    """
    両アカウントの予定を統合して取得
    
    Args:
        days_ahead: 何日先まで取得するか
        start_date: 開始日（デフォルト: 今日）
    
    Returns:
        統合された予定リスト（時系列順）
    """
    if start_date is None:
        start_date = datetime.now()
    
    accounts = ['crosslink', 'programming_school']
    all_events = []
    
    for account in accounts:
        try:
            # アカウント名の日本語化
            account_name_ja = {
                'crosslink': 'クロスリンク',
                'programming_school': 'プログラミングスクール'
            }.get(account, account)
            
            # イベント取得
            events = list_events(account, days_ahead=days_ahead)
            
            for event in events:
                # イベント情報を整形
                all_events.append({
                    'account': account,
                    'account_name': account_name_ja,
                    'title': event.get('summary', '(タイトルなし)'),
                    'start': event['start'].get('dateTime', event['start'].get('date')),
                    'end': event['end'].get('dateTime', event['end'].get('date')),
                    'location': event.get('location'),
                    'description': event.get('description'),
                    'link': event.get('htmlLink'),
                    'raw_event': event
                })
        except Exception as e:
            print(f"⚠️ Failed to fetch events for {account}: {e}")
    
    # 時系列順にソート
    all_events.sort(key=lambda x: x['start'])
    
    return all_events


def format_calendar_view(events: List[Dict[str, Any]], view_mode: str = 'list') -> str:
    """
    予定を整形して表示
    
    Args:
        events: 予定リスト
        view_mode: 表示モード（'list', 'day', 'week'）
    
    Returns:
        整形された予定表示
    """
    if not events:
        return "📅 予定がありません"
    
    if view_mode == 'list':
        return _format_list_view(events)
    elif view_mode == 'day':
        return _format_day_view(events)
    elif view_mode == 'week':
        return _format_week_view(events)
    else:
        return _format_list_view(events)


def _format_list_view(events: List[Dict[str, Any]]) -> str:
    """リスト表示"""
    result = "📅 **予定一覧**\n\n"
    
    current_date = None
    for event in events:
        # 日付の抽出
        start = event['start']
        try:
            if 'T' in start:
                dt = datetime.fromisoformat(start.replace('Z', '+00:00'))
                date_str = dt.strftime('%m/%d(%a)')
                time_str = dt.strftime('%H:%M')
            else:
                dt = datetime.fromisoformat(start)
                date_str = dt.strftime('%m/%d(%a)')
                time_str = '終日'
        except:
            date_str = start[:10]
            time_str = '?'
        
        # 日付が変わったら区切りを入れる
        if current_date != date_str:
            result += f"\n**【{date_str}】**\n"
            current_date = date_str
        
        # イベント表示
        result += f"  {time_str} - {event['title']} ({event['account_name']})\n"
        
        if event.get('location'):
            result += f"      📍 {event['location']}\n"
    
    return result


def _format_day_view(events: List[Dict[str, Any]]) -> str:
    """日表示"""
    if not events:
        return "📅 今日の予定はありません"
    
    # 今日の日付
    today = datetime.now().strftime('%m/%d(%a)')
    
    result = f"📅 **{today} の予定**\n\n"
    
    for event in events:
        start = event['start']
        try:
            if 'T' in start:
                dt = datetime.fromisoformat(start.replace('Z', '+00:00'))
                time_str = dt.strftime('%H:%M')
            else:
                time_str = '終日'
        except:
            time_str = '?'
        
        result += f"**{time_str}** - {event['title']}\n"
        result += f"  アカウント: {event['account_name']}\n"
        
        if event.get('location'):
            result += f"  場所: {event['location']}\n"
        if event.get('description'):
            desc = event['description'][:100]
            result += f"  説明: {desc}...\n" if len(event['description']) > 100 else f"  説明: {desc}\n"
        
        result += "\n"
    
    return result


def _format_week_view(events: List[Dict[str, Any]]) -> str:
    """週表示"""
    result = "📅 **今週の予定**\n\n"
    
    # 曜日ごとにグループ化
    days = {}
    for event in events:
        start = event['start']
        try:
            if 'T' in start:
                dt = datetime.fromisoformat(start.replace('Z', '+00:00'))
            else:
                dt = datetime.fromisoformat(start)
            
            day_key = dt.strftime('%m/%d(%a)')
            
            if day_key not in days:
                days[day_key] = []
            
            days[day_key].append(event)
        except:
            pass
    
    # 日付順にソート
    sorted_days = sorted(days.items(), key=lambda x: x[0])
    
    for day, day_events in sorted_days:
        result += f"\n**【{day}】** ({len(day_events)}件)\n"
        
        for event in day_events:
            start = event['start']
            try:
                if 'T' in start:
                    dt = datetime.fromisoformat(start.replace('Z', '+00:00'))
                    time_str = dt.strftime('%H:%M')
                else:
                    time_str = '終日'
            except:
                time_str = '?'
            
            result += f"  {time_str} - {event['title']} ({event['account_name']})\n"
    
    return result


def find_free_slots(
    days_ahead: int = 7,
    slot_duration_minutes: int = 60,
    work_hours: tuple = (9, 18)
) -> List[Dict[str, Any]]:
    """
    空き時間を検索
    
    Args:
        days_ahead: 何日先まで検索するか
        slot_duration_minutes: 必要な空き時間（分）
        work_hours: 営業時間（開始時, 終了時）
    
    Returns:
        空き時間のリスト
    """
    # 全予定を取得
    events = get_unified_calendar(days_ahead=days_ahead)
    
    free_slots = []
    start_hour, end_hour = work_hours
    
    # 日ごとに空き時間を検索
    for day_offset in range(days_ahead):
        current_day = datetime.now() + timedelta(days=day_offset)
        
        # 土日をスキップ（オプション）
        # if current_day.weekday() >= 5:
        #     continue
        
        # その日の予定を抽出
        day_events = [
            e for e in events
            if e['start'].startswith(current_day.strftime('%Y-%m-%d'))
        ]
        
        # 営業時間を1時間ごとに区切って空き時間を検索
        for hour in range(start_hour, end_hour):
            slot_start = current_day.replace(hour=hour, minute=0, second=0, microsecond=0)
            slot_end = slot_start + timedelta(minutes=slot_duration_minutes)
            
            # この時間帯に予定があるかチェック
            is_free = True
            for event in day_events:
                try:
                    event_start = datetime.fromisoformat(event['start'].replace('Z', '+00:00'))
                    event_end = datetime.fromisoformat(event['end'].replace('Z', '+00:00'))
                    
                    # 重複チェック
                    if not (slot_end <= event_start or slot_start >= event_end):
                        is_free = False
                        break
                except:
                    pass
            
            if is_free:
                free_slots.append({
                    'start': slot_start.isoformat(),
                    'end': slot_end.isoformat(),
                    'date': slot_start.strftime('%m/%d(%a)'),
                    'time': slot_start.strftime('%H:%M')
                })
    
    return free_slots


# CLI エントリーポイント
if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python calendar_view.py <command> [args...]")
        print("Commands:")
        print("  list [days]       - 予定一覧（デフォルト: 7日）")
        print("  today             - 今日の予定")
        print("  week              - 今週の予定")
        print("  free [days]       - 空き時間検索（デフォルト: 7日）")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == 'list':
        days = int(sys.argv[2]) if len(sys.argv) > 2 else 7
        events = get_unified_calendar(days_ahead=days)
        print(format_calendar_view(events, 'list'))
    
    elif command == 'today':
        events = get_unified_calendar(days_ahead=1)
        print(format_calendar_view(events, 'day'))
    
    elif command == 'week':
        events = get_unified_calendar(days_ahead=7)
        print(format_calendar_view(events, 'week'))
    
    elif command == 'free':
        days = int(sys.argv[2]) if len(sys.argv) > 2 else 7
        slots = find_free_slots(days_ahead=days)
        
        print(f"📅 **空き時間（{days}日間）**\n")
        if not slots:
            print("空き時間がありません")
        else:
            for slot in slots[:20]:  # 最大20件
                print(f"  {slot['date']} {slot['time']} - {slot['end']}")
    
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)
