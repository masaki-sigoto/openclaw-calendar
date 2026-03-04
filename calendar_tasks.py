#!/usr/bin/env python3
"""
Google Tasks 連携
カレンダーとタスクの統合管理
"""

import sys
import os
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from openclaw_helper import get_mcp, create_task, list_tasks


def create_task_with_calendar(
    account: str,
    title: str,
    due_date: Optional[str] = None,
    notes: Optional[str] = None,
    add_to_calendar: bool = True
) -> Dict[str, Any]:
    """
    タスクを作成し、オプションでカレンダーにも追加
    
    Args:
        account: 'crosslink' or 'programming_school'
        title: タスクのタイトル
        due_date: 期限（ISO 8601形式）
        notes: メモ
        add_to_calendar: カレンダーにも追加するか
    
    Returns:
        作成結果
    """
    # Google Tasks にタスクを作成
    task = create_task(
        account=account,
        title=title,
        due=due_date,
        notes=notes
    )
    
    result = {
        'success': True,
        'task': task,
        'calendar_event': None
    }
    
    # カレンダーにも追加
    if add_to_calendar and due_date:
        try:
            from openclaw_helper import create_event
            
            # 期限日の終日イベントとして追加
            # RFC 3339 → ISO 8601 形式に変換
            due_date_only = due_date.split('T')[0]
            next_day = (datetime.fromisoformat(due_date_only) + timedelta(days=1)).strftime('%Y-%m-%d')
            
            event = create_event(
                account=account,
                title=f"📝 {title}（タスク期限）",
                start=due_date_only,
                end=next_day,
                description=notes or ''
            )
            
            result['calendar_event'] = event
        except Exception as e:
            print(f"⚠️ Failed to add to calendar: {e}")
    
    return result


def get_unified_tasks_and_events(
    account: Optional[str] = None,
    days_ahead: int = 7
) -> Dict[str, List[Dict[str, Any]]]:
    """
    タスクとカレンダーを統合して取得
    
    Args:
        account: 特定のアカウントのみ（オプション）
        days_ahead: 何日先まで取得するか
    
    Returns:
        {'tasks': [...], 'events': [...]}
    """
    from calendar_view import get_unified_calendar
    
    accounts = [account] if account else ['crosslink', 'programming_school']
    
    all_tasks = []
    for acc in accounts:
        try:
            tasks = list_tasks(acc)
            
            for task in tasks:
                all_tasks.append({
                    'account': acc,
                    'account_name': 'クロスリンク' if acc == 'crosslink' else 'プログラミングスクール',
                    'title': task.get('title', '(タイトルなし)'),
                    'due': task.get('due'),
                    'status': task.get('status'),
                    'notes': task.get('notes'),
                    'raw_task': task
                })
        except Exception as e:
            print(f"⚠️ Failed to fetch tasks for {acc}: {e}")
    
    # カレンダーも取得
    all_events = get_unified_calendar(days_ahead=days_ahead)
    
    return {
        'tasks': all_tasks,
        'events': all_events
    }


def suggest_time_blocks_for_tasks(
    days_ahead: int = 7,
    task_duration: int = 60
) -> List[Dict[str, Any]]:
    """
    タスク実行のための時間ブロックを提案
    
    Args:
        days_ahead: 何日先まで検索するか
        task_duration: タスク1つあたりの所要時間（分）
    
    Returns:
        提案リスト
    """
    from calendar_view import find_free_slots
    
    # 空き時間を検索
    free_slots = find_free_slots(
        days_ahead=days_ahead,
        slot_duration_minutes=task_duration
    )
    
    # 提案を作成
    suggestions = []
    for slot in free_slots[:10]:
        suggestions.append({
            'date': slot['date'],
            'time': slot['time'],
            'start': slot['start'],
            'end': slot['end'],
            'purpose': 'タスク実行時間'
        })
    
    return suggestions


def format_unified_view(data: Dict[str, List[Dict[str, Any]]]) -> str:
    """
    統合ビューをフォーマット
    
    Args:
        data: タスクとイベントのデータ
    
    Returns:
        フォーマットされたテキスト
    """
    result = "📋 **タスク & カレンダー 統合ビュー**\n\n"
    
    # タスク
    tasks = data['tasks']
    if tasks:
        result += f"**📝 タスク（{len(tasks)}件）**\n\n"
        
        # 期限でソート
        tasks_with_due = [t for t in tasks if t.get('due')]
        tasks_without_due = [t for t in tasks if not t.get('due')]
        
        tasks_with_due.sort(key=lambda x: x['due'])
        
        for task in tasks_with_due[:10]:
            due = task['due']
            try:
                due_dt = datetime.fromisoformat(due.replace('Z', '+00:00'))
                due_str = due_dt.strftime('%m/%d')
            except:
                due_str = due[:10]
            
            result += f"  ⏰ {due_str} - {task['title']}\n"
            result += f"     ({task['account_name']})\n"
        
        if tasks_without_due:
            result += f"\n  期限なし: {len(tasks_without_due)}件\n"
        
        result += "\n"
    else:
        result += "**📝 タスク**\nタスクはありません\n\n"
    
    # カレンダー
    events = data['events']
    if events:
        result += f"**📅 今後の予定（{len(events)}件）**\n\n"
        
        current_date = None
        for event in events[:10]:
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
            
            if current_date != date_str:
                result += f"\n{date_str}\n"
                current_date = date_str
            
            result += f"  {time_str} - {event['title']}\n"
    else:
        result += "**📅 今後の予定**\n予定はありません\n"
    
    return result


# CLI エントリーポイント
if __name__ == '__main__':
    import json
    
    if len(sys.argv) < 2:
        print("Usage: python calendar_tasks.py <command> [args...]")
        print("Commands:")
        print("  create <account> <title> [due] [notes]  - タスクを作成")
        print("  list [account]                          - タスク一覧")
        print("  unified [account] [days]                - タスク & カレンダー統合表示")
        print("  suggest [days] [duration]               - タスク実行時間を提案")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == 'create':
        account = sys.argv[2]
        title = sys.argv[3]
        due = sys.argv[4] if len(sys.argv) > 4 else None
        notes = sys.argv[5] if len(sys.argv) > 5 else None
        
        result = create_task_with_calendar(account, title, due, notes)
        
        print(f"✅ タスクを作成しました\n")
        print(f"タイトル: {title}")
        if due:
            print(f"期限: {due}")
        if result['calendar_event']:
            print(f"カレンダーにも追加しました")
    
    elif command == 'list':
        account = sys.argv[2] if len(sys.argv) > 2 else None
        
        accounts = [account] if account else ['crosslink', 'programming_school']
        
        for acc in accounts:
            account_name = 'クロスリンク' if acc == 'crosslink' else 'プログラミングスクール'
            print(f"\n【{account_name}】")
            
            tasks = list_tasks(acc)
            
            if not tasks:
                print("  タスクなし")
            else:
                for task in tasks:
                    print(f"  - {task.get('title', '(タイトルなし)')}")
                    if task.get('due'):
                        print(f"    期限: {task['due']}")
    
    elif command == 'unified':
        account = sys.argv[2] if len(sys.argv) > 2 and sys.argv[2] in ['crosslink', 'programming_school'] else None
        days = int(sys.argv[3]) if len(sys.argv) > 3 else 7
        
        data = get_unified_tasks_and_events(account=account, days_ahead=days)
        print(format_unified_view(data))
    
    elif command == 'suggest':
        days = int(sys.argv[2]) if len(sys.argv) > 2 else 7
        duration = int(sys.argv[3]) if len(sys.argv) > 3 else 60
        
        suggestions = suggest_time_blocks_for_tasks(days_ahead=days, task_duration=duration)
        
        print(f"💡 **タスク実行に最適な時間（{len(suggestions)}件）**\n")
        for i, slot in enumerate(suggestions, 1):
            print(f"{i}. {slot['date']} {slot['time']}")
    
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)
