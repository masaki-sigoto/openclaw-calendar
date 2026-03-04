#!/usr/bin/env python3
"""
カレンダー編集機能
予定の削除・編集
"""

import sys
import os
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from openclaw_helper import get_mcp
from calendar_view import get_unified_calendar


def search_events(
    query: str,
    account: Optional[str] = None,
    days_ahead: int = 30
) -> List[Dict[str, Any]]:
    """
    予定を検索
    
    Args:
        query: 検索クエリ（タイトルの一部）
        account: 特定のアカウントのみ検索（オプション）
        days_ahead: 何日先まで検索するか
    
    Returns:
        マッチした予定のリスト
    """
    # 全予定を取得
    all_events = get_unified_calendar(days_ahead=days_ahead)
    
    # フィルタリング
    results = []
    for event in all_events:
        # アカウント指定があればフィルタ
        if account and event['account'] != account:
            continue
        
        # タイトルで検索
        if query.lower() in event['title'].lower():
            results.append(event)
    
    return results


def delete_event(
    event_id: str,
    account: str
) -> bool:
    """
    予定を削除
    
    Args:
        event_id: Google Calendar のイベントID
        account: アカウント名
    
    Returns:
        削除成功したかどうか
    """
    try:
        mcp = get_mcp()
        
        if account not in mcp.services:
            mcp.authenticate(account)
        
        calendar_service = mcp.services[account]['calendar']
        calendar_service.events().delete(
            calendarId='primary',
            eventId=event_id
        ).execute()
        
        return True
    except Exception as e:
        print(f"⚠️ Failed to delete event: {e}")
        return False


def delete_event_by_title(
    title_query: str,
    account: Optional[str] = None,
    confirm: bool = True
) -> Dict[str, Any]:
    """
    タイトルで検索して予定を削除
    
    Args:
        title_query: タイトルの検索クエリ
        account: 特定のアカウントのみ検索（オプション）
        confirm: 削除前に確認するかどうか
    
    Returns:
        削除結果
    """
    # 予定を検索
    matches = search_events(title_query, account=account)
    
    if not matches:
        return {
            'success': False,
            'message': f'「{title_query}」に一致する予定が見つかりませんでした'
        }
    
    if len(matches) > 1 and confirm:
        # 複数ヒット → ユーザーに選択させる
        return {
            'success': False,
            'needs_selection': True,
            'matches': matches,
            'message': f'「{title_query}」に一致する予定が{len(matches)}件見つかりました。どれを削除しますか？'
        }
    
    # 1件のみヒット → 削除
    event = matches[0]
    event_id = event['raw_event']['id']
    
    success = delete_event(event_id, event['account'])
    
    if success:
        return {
            'success': True,
            'deleted_event': event,
            'message': f"✅ 削除しました\n\n"
                      f"タイトル: {event['title']}\n"
                      f"日時: {event['start']}\n"
                      f"アカウント: {event['account_name']}"
        }
    else:
        return {
            'success': False,
            'message': '削除に失敗しました'
        }


def update_event(
    event_id: str,
    account: str,
    updates: Dict[str, Any]
) -> bool:
    """
    予定を更新
    
    Args:
        event_id: Google Calendar のイベントID
        account: アカウント名
        updates: 更新内容（'summary', 'start', 'end', 'location', 'description' など）
    
    Returns:
        更新成功したかどうか
    """
    try:
        mcp = get_mcp()
        
        if account not in mcp.services:
            mcp.authenticate(account)
        
        calendar_service = mcp.services[account]['calendar']
        
        # 既存のイベントを取得
        event = calendar_service.events().get(
            calendarId='primary',
            eventId=event_id
        ).execute()
        
        # 更新を適用
        if 'summary' in updates:
            event['summary'] = updates['summary']
        
        if 'start' in updates:
            if 'T' in updates['start']:
                event['start'] = {'dateTime': updates['start'], 'timeZone': 'Asia/Tokyo'}
            else:
                event['start'] = {'date': updates['start']}
        
        if 'end' in updates:
            if 'T' in updates['end']:
                event['end'] = {'dateTime': updates['end'], 'timeZone': 'Asia/Tokyo'}
            else:
                event['end'] = {'date': updates['end']}
        
        if 'location' in updates:
            event['location'] = updates['location']
        
        if 'description' in updates:
            event['description'] = updates['description']
        
        # 更新を送信
        updated_event = calendar_service.events().update(
            calendarId='primary',
            eventId=event_id,
            body=event
        ).execute()
        
        return True
    except Exception as e:
        print(f"⚠️ Failed to update event: {e}")
        return False


def update_event_by_title(
    title_query: str,
    updates: Dict[str, Any],
    account: Optional[str] = None
) -> Dict[str, Any]:
    """
    タイトルで検索して予定を更新
    
    Args:
        title_query: タイトルの検索クエリ
        updates: 更新内容
        account: 特定のアカウントのみ検索（オプション）
    
    Returns:
        更新結果
    """
    # 予定を検索
    matches = search_events(title_query, account=account)
    
    if not matches:
        return {
            'success': False,
            'message': f'「{title_query}」に一致する予定が見つかりませんでした'
        }
    
    if len(matches) > 1:
        # 複数ヒット → ユーザーに選択させる
        return {
            'success': False,
            'needs_selection': True,
            'matches': matches,
            'message': f'「{title_query}」に一致する予定が{len(matches)}件見つかりました。どれを更新しますか？'
        }
    
    # 1件のみヒット → 更新
    event = matches[0]
    event_id = event['raw_event']['id']
    
    success = update_event(event_id, event['account'], updates)
    
    if success:
        return {
            'success': True,
            'updated_event': event,
            'updates': updates,
            'message': f"✅ 更新しました\n\n"
                      f"タイトル: {event['title']}\n"
                      f"アカウント: {event['account_name']}\n"
                      f"変更内容: {', '.join(updates.keys())}"
        }
    else:
        return {
            'success': False,
            'message': '更新に失敗しました'
        }


# CLI エントリーポイント
if __name__ == '__main__':
    import json
    
    if len(sys.argv) < 2:
        print("Usage: python calendar_edit.py <command> [args...]")
        print("Commands:")
        print("  search <query> [account]           - 予定を検索")
        print("  delete <query> [account]           - 予定を削除")
        print("  update <query> <field> <value>     - 予定を更新")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == 'search':
        query = sys.argv[2]
        account = sys.argv[3] if len(sys.argv) > 3 else None
        
        results = search_events(query, account=account)
        
        if not results:
            print(f'「{query}」に一致する予定が見つかりませんでした')
        else:
            print(f'🔍 「{query}」の検索結果（{len(results)}件）\n')
            for i, event in enumerate(results, 1):
                print(f"{i}. {event['title']}")
                print(f"   日時: {event['start']}")
                print(f"   アカウント: {event['account_name']}")
                print()
    
    elif command == 'delete':
        query = sys.argv[2]
        account = sys.argv[3] if len(sys.argv) > 3 else None
        
        result = delete_event_by_title(query, account=account)
        print(result['message'])
        
        if result.get('needs_selection'):
            print('\n候補:')
            for i, event in enumerate(result['matches'], 1):
                print(f"{i}. {event['title']} ({event['start']})")
    
    elif command == 'update':
        query = sys.argv[2]
        field = sys.argv[3]
        value = sys.argv[4]
        
        updates = {field: value}
        result = update_event_by_title(query, updates)
        print(result['message'])
    
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)
