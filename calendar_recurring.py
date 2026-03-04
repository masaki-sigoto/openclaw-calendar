#!/usr/bin/env python3
"""
定期予定の管理
繰り返しイベントの作成・管理
"""

import sys
import os
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from openclaw_helper import get_mcp
from openclaw_integration import notify_calendar_event


def parse_recurrence_rule(pattern: str) -> tuple[str, Dict[str, Any]]:
    """
    自然言語から繰り返しルールを生成
    
    Args:
        pattern: 「毎週水曜」「毎月第1金曜」「毎日」など
    
    Returns:
        (rrule, metadata): RFC 5545形式のルール + メタデータ
    
    Examples:
        >>> parse_recurrence_rule('毎週水曜')
        ('RRULE:FREQ=WEEKLY;BYDAY=WE', {'frequency': 'weekly', 'day': 'Wednesday'})
        >>> parse_recurrence_rule('毎月第1金曜')
        ('RRULE:FREQ=MONTHLY;BYDAY=1FR', {'frequency': 'monthly', 'week': 1, 'day': 'Friday'})
    """
    pattern = pattern.lower()
    
    # 毎日
    if '毎日' in pattern:
        return ('RRULE:FREQ=DAILY', {'frequency': 'daily'})
    
    # 毎週
    if '毎週' in pattern:
        day_map = {
            '月': 'MO', '月曜': 'MO',
            '火': 'TU', '火曜': 'TU',
            '水': 'WE', '水曜': 'WE',
            '木': 'TH', '木曜': 'TH',
            '金': 'FR', '金曜': 'FR',
            '土': 'SA', '土曜': 'SA',
            '日': 'SU', '日曜': 'SU'
        }
        
        for day_ja, day_en in day_map.items():
            if day_ja in pattern:
                return (f'RRULE:FREQ=WEEKLY;BYDAY={day_en}', 
                       {'frequency': 'weekly', 'day': day_ja})
    
    # 毎月
    if '毎月' in pattern:
        # 第N週の曜日
        week_map = {'第1': '1', '第2': '2', '第3': '3', '第4': '4', '最終': '-1'}
        day_map = {
            '月': 'MO', '月曜': 'MO',
            '火': 'TU', '火曜': 'TU',
            '水': 'WE', '水曜': 'WE',
            '木': 'TH', '木曜': 'TH',
            '金': 'FR', '金曜': 'FR',
            '土': 'SA', '土曜': 'SA',
            '日': 'SU', '日曜': 'SU'
        }
        
        for week_ja, week_num in week_map.items():
            if week_ja in pattern:
                for day_ja, day_en in day_map.items():
                    if day_ja in pattern:
                        return (f'RRULE:FREQ=MONTHLY;BYDAY={week_num}{day_en}',
                               {'frequency': 'monthly', 'week': week_num, 'day': day_ja})
        
        # 日付指定（例: 毎月15日）
        import re
        date_match = re.search(r'(\d+)日', pattern)
        if date_match:
            day = date_match.group(1)
            return (f'RRULE:FREQ=MONTHLY;BYMONTHDAY={day}',
                   {'frequency': 'monthly', 'day': int(day)})
    
    # デフォルト: 毎週（曜日が指定されていない場合）
    return ('RRULE:FREQ=WEEKLY', {'frequency': 'weekly'})


def create_recurring_event(
    account: str,
    title: str,
    start_time: str,
    end_time: str,
    recurrence_pattern: str,
    until: Optional[str] = None,
    count: Optional[int] = None,
    description: Optional[str] = None,
    location: Optional[str] = None
) -> Dict[str, Any]:
    """
    定期予定を作成
    
    Args:
        account: 'crosslink' or 'programming_school'
        title: イベントのタイトル
        start_time: 開始時刻（ISO 8601形式）
        end_time: 終了時刻
        recurrence_pattern: 繰り返しパターン（「毎週水曜」など）
        until: 終了日（ISO 8601形式、オプション）
        count: 繰り返し回数（オプション）
        description: 説明（オプション）
        location: 場所（オプション）
    
    Returns:
        作成されたイベントの情報
    
    Examples:
        >>> create_recurring_event(
        ...     account='crosslink',
        ...     title='チームMTG',
        ...     start_time='2026-03-05T10:00:00+09:00',
        ...     end_time='2026-03-05T11:00:00+09:00',
        ...     recurrence_pattern='毎週水曜'
        ... )
    """
    mcp = get_mcp()
    
    if account not in mcp.services:
        mcp.authenticate(account)
    
    # 繰り返しルールを生成
    rrule, metadata = parse_recurrence_rule(recurrence_pattern)
    
    # 終了条件を追加
    if until:
        # ISO 8601 → YYYYMMDD 形式に変換
        until_date = until.replace('-', '').split('T')[0]
        rrule += f';UNTIL={until_date}'
    elif count:
        rrule += f';COUNT={count}'
    
    # 終日イベントかどうかを判定
    is_all_day = 'T' not in start_time
    
    # イベント作成
    if is_all_day:
        event_body = {
            'summary': title,
            'start': {'date': start_time, 'timeZone': 'Asia/Tokyo'},
            'end': {'date': end_time, 'timeZone': 'Asia/Tokyo'},
            'recurrence': [rrule]
        }
    else:
        event_body = {
            'summary': title,
            'start': {'dateTime': start_time, 'timeZone': 'Asia/Tokyo'},
            'end': {'dateTime': end_time, 'timeZone': 'Asia/Tokyo'},
            'recurrence': [rrule]
        }
    
    if description:
        event_body['description'] = description
    if location:
        event_body['location'] = location
    
    calendar_service = mcp.services[account]['calendar']
    event = calendar_service.events().insert(
        calendarId='primary',
        body=event_body
    ).execute()
    
    # 通知送信
    notify_calendar_event(
        account=account,
        title=f"{title}（{recurrence_pattern}）",
        start_time=start_time,
        end_time=end_time,
        event_link=event.get('htmlLink')
    )
    
    return {
        'success': True,
        'event': event,
        'recurrence': metadata,
        'message': f"✅ 定期予定を作成しました\n\n"
                  f"タイトル: {title}\n"
                  f"繰り返し: {recurrence_pattern}\n"
                  f"日時: {start_time} - {end_time}\n"
                  f"リンク: {event.get('htmlLink')}"
    }


def create_recurring_from_text(text: str) -> Dict[str, Any]:
    """
    自然言語から定期予定を作成
    
    Args:
        text: 「毎週水曜10時にチームMTG、1時間」など
    
    Returns:
        作成結果
    
    Examples:
        >>> create_recurring_from_text('毎週水曜10時にチームMTG、1時間')
        >>> create_recurring_from_text('毎月第1金曜15時にレポート提出、30分')
    """
    import re
    from openclaw_helper import determine_account
    
    # アカウント判定
    account, is_explicit = determine_account(text)
    
    # 繰り返しパターンを抽出
    patterns = ['毎日', '毎週月', '毎週火', '毎週水', '毎週木', '毎週金', '毎週土', '毎週日',
                '毎月第1', '毎月第2', '毎月第3', '毎月第4', '毎月最終']
    
    recurrence_pattern = None
    
    # より具体的なパターンから順に検索（長いパターン優先）
    week_patterns = ['毎週月曜', '毎週火曜', '毎週水曜', '毎週木曜', '毎週金曜', '毎週土曜', '毎週日曜']
    month_patterns = ['毎月第1月曜', '毎月第1火曜', '毎月第1水曜', '毎月第1木曜', '毎月第1金曜',
                     '毎月第2月曜', '毎月第2火曜', '毎月第2水曜', '毎月第2木曜', '毎月第2金曜',
                     '毎月第3月曜', '毎月第3火曜', '毎月第3水曜', '毎月第3木曜', '毎月第3金曜',
                     '毎月第4月曜', '毎月第4火曜', '毎月第4水曜', '毎月第4木曜', '毎月第4金曜',
                     '毎月最終月曜', '毎月最終火曜', '毎月最終水曜', '毎月最終木曜', '毎月最終金曜']
    
    # 月パターンを優先（より具体的）
    for pattern in month_patterns:
        if pattern in text:
            recurrence_pattern = pattern
            break
    
    # 週パターン
    if not recurrence_pattern:
        for pattern in week_patterns:
            if pattern in text:
                recurrence_pattern = pattern
                break
    
    # 毎日
    if not recurrence_pattern and '毎日' in text:
        recurrence_pattern = '毎日'
    
    if not recurrence_pattern:
        return {
            'success': False,
            'message': '繰り返しパターンが見つかりません。「毎週〇曜」または「毎月第N〇曜」を指定してください。'
        }
    
    # 時刻を抽出
    time_match = re.search(r'(\d{1,2})[:時](\d{1,2})?', text)
    if not time_match:
        return {
            'success': False,
            'message': '開始時刻が見つかりません'
        }
    
    hour = int(time_match.group(1))
    minute = int(time_match.group(2)) if time_match.group(2) else 0
    
    # 次回の開始日を計算
    # 例: 「毎週水曜」なら、次の水曜日
    from datetime import datetime, timedelta
    now = datetime.now()
    
    # 曜日マップ
    weekday_map = {
        '月曜': 0, '火曜': 1, '水曜': 2, '木曜': 3,
        '金曜': 4, '土曜': 5, '日曜': 6
    }
    
    # 次回の日付を計算
    if '毎週' in recurrence_pattern:
        for day_ja, weekday in weekday_map.items():
            if day_ja in recurrence_pattern:
                days_ahead = (weekday - now.weekday()) % 7
                if days_ahead == 0:
                    days_ahead = 7  # 今日が該当日なら来週
                next_date = now + timedelta(days=days_ahead)
                break
    else:
        # 毎月の場合は来月の該当日
        next_date = now + timedelta(days=30)
    
    start_time = next_date.replace(hour=hour, minute=minute, second=0, microsecond=0)
    
    # 時間を抽出
    duration_match = re.search(r'(\d+)\s*(時間|分|h|min)', text)
    if duration_match:
        duration = int(duration_match.group(1))
        unit = duration_match.group(2)
        
        if unit in ['時間', 'h']:
            end_time = start_time + timedelta(hours=duration)
        else:
            end_time = start_time + timedelta(minutes=duration)
    else:
        # デフォルト: 1時間
        end_time = start_time + timedelta(hours=1)
    
    # タイトルを抽出
    title = text.split('、')[0].split('。')[0]
    # 繰り返しパターンと時刻表現を削除
    title = re.sub(r'毎[週月日][^、。\s]*', '', title)
    title = re.sub(r'\d+[:時]\d*', '', title)
    title = re.sub(r'(\d+)\s*(時間|分)', '', title)
    title = title.strip()
    
    # 定期予定を作成
    return create_recurring_event(
        account=account,
        title=title,
        start_time=start_time.strftime('%Y-%m-%dT%H:%M:%S+09:00'),
        end_time=end_time.strftime('%Y-%m-%dT%H:%M:%S+09:00'),
        recurrence_pattern=recurrence_pattern
    )


# CLI エントリーポイント
if __name__ == '__main__':
    import json
    
    if len(sys.argv) < 2:
        print("Usage: python calendar_recurring.py <command> [args...]")
        print("Commands:")
        print("  create <account> <title> <start> <end> <pattern>  - 定期予定を作成")
        print("  from-text <text>                                   - 自然言語で作成")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == 'create':
        account = sys.argv[2]
        title = sys.argv[3]
        start = sys.argv[4]
        end = sys.argv[5]
        pattern = sys.argv[6]
        
        result = create_recurring_event(account, title, start, end, pattern)
        print(result['message'])
    
    elif command == 'from-text':
        text = ' '.join(sys.argv[2:])
        result = create_recurring_from_text(text)
        print(result.get('message', json.dumps(result, indent=2, ensure_ascii=False)))
    
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)
