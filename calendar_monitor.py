#!/usr/bin/env python3
"""
カレンダー監視スクリプト
定期的にGoogleカレンダーをチェックして、新しいイベントを通知
"""

import os
import sys
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from openclaw_helper import list_events, get_mcp
from openclaw_integration import notify_calendar_event

# 状態ファイルのパス
STATE_FILE = os.path.join(os.path.dirname(__file__), 'calendar_monitor_state.json')


def load_state() -> Dict[str, Any]:
    """前回のチェック状態を読み込む"""
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            pass
    
    # デフォルト状態
    return {
        'last_check': None,
        'seen_events': {}  # {account: [event_id, ...]}
    }


def save_state(state: Dict[str, Any]):
    """現在の状態を保存"""
    with open(STATE_FILE, 'w', encoding='utf-8') as f:
        json.dump(state, f, indent=2, ensure_ascii=False)


def check_new_events(account: str, state: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    新しいイベントをチェック
    
    Args:
        account: 'crosslink' or 'programming_school'
        state: 前回のチェック状態
    
    Returns:
        新しいイベントのリスト
    """
    # 前回チェック時刻以降のイベントを取得
    last_check = state.get('last_check')
    if last_check:
        last_check_dt = datetime.fromisoformat(last_check)
        # 前回チェックから5分前までのイベントを取得（重複を防ぐため少し余裕を持たせる）
        time_min = (last_check_dt - timedelta(minutes=5)).isoformat() + 'Z'
    else:
        # 初回チェックは今から24時間先までのイベントを取得
        time_min = datetime.utcnow().isoformat() + 'Z'
    
    # カレンダーイベントを取得
    try:
        mcp = get_mcp()
        if account not in mcp.services:
            mcp.authenticate(account)
        
        calendar_service = mcp.services[account]['calendar']
        time_max = (datetime.utcnow() + timedelta(days=30)).isoformat() + 'Z'
        
        events_result = calendar_service.events().list(
            calendarId='primary',
            timeMin=time_min,
            timeMax=time_max,
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        
        events = events_result.get('items', [])
    except Exception as e:
        print(f"⚠️ Failed to fetch events for {account}: {e}")
        return []
    
    # 前回見たイベントIDのセット
    seen_events = set(state.get('seen_events', {}).get(account, []))
    
    # 新しいイベントのみをフィルタ
    new_events = []
    for event in events:
        event_id = event['id']
        
        # 既に見たイベントはスキップ
        if event_id in seen_events:
            continue
        
        # 作成時刻をチェック（自分で作成したイベントは通知しない）
        created = event.get('created')
        if created:
            created_dt = datetime.fromisoformat(created.replace('Z', '+00:00'))
            # 最近5分以内に作成されたイベントはスキップ（OpenClawから作成したイベント）
            if (datetime.now(created_dt.tzinfo) - created_dt).total_seconds() < 300:
                # でも seen_events には追加しておく
                seen_events.add(event_id)
                continue
        
        new_events.append(event)
        seen_events.add(event_id)
    
    # 状態を更新
    if account not in state.get('seen_events', {}):
        state['seen_events'] = state.get('seen_events', {})
    state['seen_events'][account] = list(seen_events)
    
    return new_events


def monitor_calendars():
    """両方のアカウントのカレンダーを監視"""
    state = load_state()
    
    # 初回実行かどうかを判定
    is_first_run = state.get('last_check') is None
    
    accounts = ['crosslink', 'programming_school']
    all_new_events = []
    
    for account in accounts:
        print(f"📅 Checking {account}...")
        new_events = check_new_events(account, state)
        
        if new_events:
            if is_first_run:
                print(f"  ℹ️ First run: Found {len(new_events)} existing event(s), marking as seen (not notifying)")
            else:
                print(f"  ✅ Found {len(new_events)} new event(s)")
                for event in new_events:
                    all_new_events.append({
                        'account': account,
                        'event': event
                    })
        else:
            print(f"  ℹ️ No new events")
    
    # 現在時刻を保存
    state['last_check'] = datetime.utcnow().isoformat()
    save_state(state)
    
    # 初回実行の場合は通知しない
    if is_first_run:
        print("\n✅ First run completed. Existing events marked as seen. Future runs will notify new events only.")
        return
    
    # 新しいイベントを通知
    for item in all_new_events:
        account = item['account']
        event = item['event']
        
        title = event.get('summary', '(タイトルなし)')
        start = event['start'].get('dateTime', event['start'].get('date'))
        end = event['end'].get('dateTime', event['end'].get('date'))
        event_link = event.get('htmlLink')
        
        print(f"\n🔔 Notifying: {title} ({account})")
        
        # 通知送信
        notify_calendar_event(
            account=account,
            title=title,
            start_time=start,
            end_time=end,
            event_link=event_link
        )
    
    if all_new_events:
        print(f"\n✅ Notified {len(all_new_events)} new event(s)")
    else:
        print("\n✅ No new events to notify")


if __name__ == '__main__':
    monitor_calendars()
