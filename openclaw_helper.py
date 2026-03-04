#!/usr/bin/env python3
"""
OpenClaw ヘルパー関数
OpenClaw から Google Calendar MCP を簡単に使うためのラッパー
"""

import os
import sys
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List

# カレンダーサーバーをインポート
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from server import GoogleCalendarMCP


# グローバルインスタンス
_mcp = None


def get_mcp() -> GoogleCalendarMCP:
    """MCPインスタンスを取得（シングルトン）"""
    global _mcp
    if _mcp is None:
        _mcp = GoogleCalendarMCP()
    return _mcp


def ensure_authenticated(account: str):
    """認証を確認（必要なら自動認証）"""
    mcp = get_mcp()
    if account not in mcp.services:
        mcp.authenticate(account)


def create_event(
    account: str,
    title: str,
    start: str,
    end: str,
    description: Optional[str] = None,
    location: Optional[str] = None
) -> Dict[str, Any]:
    """
    カレンダーイベントを作成
    
    Args:
        account: 'crosslink' or 'programming_school'
        title: イベントのタイトル
        start: 開始時刻（ISO 8601形式）
        end: 終了時刻（ISO 8601形式）
        description: 説明（オプション）
        location: 場所（オプション）
    
    Returns:
        作成されたイベントの情報
    
    Example:
        >>> create_event(
        ...     account='crosslink',
        ...     title='A社 定例MTG',
        ...     start='2026-03-05T14:00:00+09:00',
        ...     end='2026-03-05T15:00:00+09:00'
        ... )
    """
    mcp = get_mcp()
    ensure_authenticated(account)
    
    return mcp.create_event(
        account=account,
        summary=title,
        start_time=start,
        end_time=end,
        description=description,
        location=location
    )


def list_events(
    account: str,
    days_ahead: int = 7
) -> List[Dict[str, Any]]:
    """
    今後のカレンダーイベントを取得
    
    Args:
        account: 'crosslink' or 'programming_school'
        days_ahead: 何日先まで取得するか（デフォルト: 7日）
    
    Returns:
        イベントのリスト
    
    Example:
        >>> events = list_events('crosslink', days_ahead=3)
        >>> for event in events:
        ...     print(f"{event['start']['dateTime']}: {event['summary']}")
    """
    mcp = get_mcp()
    ensure_authenticated(account)
    
    time_max = (datetime.utcnow() + timedelta(days=days_ahead)).isoformat() + 'Z'
    
    return mcp.list_events(
        account=account,
        time_max=time_max
    )


def create_task(
    account: str,
    title: str,
    due: Optional[str] = None,
    notes: Optional[str] = None
) -> Dict[str, Any]:
    """
    Google Tasksにタスクを作成
    
    Args:
        account: 'crosslink' or 'programming_school'
        title: タスクのタイトル
        due: 期限（RFC 3339形式）
        notes: メモ（オプション）
    
    Returns:
        作成されたタスクの情報
    
    Example:
        >>> create_task(
        ...     account='crosslink',
        ...     title='提案書作成',
        ...     due='2026-03-10T00:00:00Z'
        ... )
    """
    mcp = get_mcp()
    ensure_authenticated(account)
    
    return mcp.create_task(
        account=account,
        title=title,
        due=due,
        notes=notes
    )


def list_tasks(account: str) -> List[Dict[str, Any]]:
    """
    Google Tasksのタスク一覧を取得
    
    Args:
        account: 'crosslink' or 'programming_school'
    
    Returns:
        タスクのリスト
    
    Example:
        >>> tasks = list_tasks('crosslink')
        >>> for task in tasks:
        ...     print(f"{task['title']}")
    """
    mcp = get_mcp()
    ensure_authenticated(account)
    
    return mcp.list_tasks(account=account)


def determine_account(text: str) -> tuple[str, bool]:
    """
    自然言語から適切なアカウントを判定
    
    Args:
        text: ユーザーの入力テキスト
    
    Returns:
        (account, is_explicit): アカウント名と、明示的に指定されたかどうか
    
    Example:
        >>> determine_account("明日A社と打ち合わせ")
        ('crosslink', False)  # キーワード判定
        >>> determine_account("クロスリンクで明日MTG")
        ('crosslink', True)   # 明示的指定
    """
    return _determine_account_internal(text)


def _determine_account_internal(text: str) -> tuple[str, bool]:
    """
    自然言語から適切なアカウントを判定
    
    Args:
        text: ユーザーの入力テキスト
    
    Returns:
        'crosslink' or 'programming_school'
    
    Example:
        >>> determine_account("明日A社と打ち合わせ")
        'crosslink'
        >>> determine_account("ココグラムの座席表作成")
        'programming_school'
        >>> determine_account("クロスリンクのアカウントでイベント登録")
        'crosslink'
        >>> determine_account("プログラミングスクールで登録")
        'programming_school'
    """
    text_lower = text.lower()
    
    # 明示的なアカウント指定をチェック（最優先）
    explicit_crosslink = [
        'クロスリンクのアカウント', 'クロスリンクで', 'クロスリンク側',
        'm-nakano@crosslink', 'crosslink'
    ]
    explicit_programming = [
        'プログラミングスクールのアカウント', 'プログラミングスクールで', 'プログラミング側',
        'masaki.kozinn', 'programming_school', 'プログラミングスクール'
    ]
    
    for keyword in explicit_crosslink:
        if keyword in text_lower:
            return ('crosslink', True)  # 明示的指定
    
    for keyword in explicit_programming:
        if keyword in text_lower:
            return ('programming_school', True)  # 明示的指定
    
    # キーワードベースの自動判定
    crosslink_keywords = [
        'a社', 'b社', '営業', '商談', '提案',
        'ラーニング', 'seo', 'ブログ', '記事',
        'プロシーズ', 'サンヴァーテックス'
    ]
    
    programming_keywords = [
        '体験会', 'ココグラム', '座席表', 'シフト',
        '名古屋', '関西', '東海', '一宮', '門真'
    ]
    
    # キーワードマッチング
    crosslink_score = sum(1 for kw in crosslink_keywords if kw in text_lower)
    programming_score = sum(1 for kw in programming_keywords if kw in text_lower)
    
    if crosslink_score > programming_score:
        return ('crosslink', False)  # キーワード判定
    elif programming_score > crosslink_score:
        return ('programming_school', False)  # キーワード判定
    else:
        # デフォルトはクロスリンク
        return ('crosslink', False)  # キーワード判定


# CLI エントリーポイント
if __name__ == '__main__':
    import json
    
    if len(sys.argv) < 2:
        print("Usage: python openclaw_helper.py <command> [args...]")
        print("Commands:")
        print("  create <account> <title> <start> <end> [description] [location]")
        print("  list <account> [days_ahead]")
        print("  task <account> <title> [due] [notes]")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == 'create':
        account = sys.argv[2]
        title = sys.argv[3]
        start = sys.argv[4]
        end = sys.argv[5]
        description = sys.argv[6] if len(sys.argv) > 6 else None
        location = sys.argv[7] if len(sys.argv) > 7 else None
        
        event = create_event(account, title, start, end, description, location)
        print(json.dumps(event, indent=2, ensure_ascii=False))
    
    elif command == 'list':
        account = sys.argv[2]
        days_ahead = int(sys.argv[3]) if len(sys.argv) > 3 else 7
        
        events = list_events(account, days_ahead)
        print(json.dumps(events, indent=2, ensure_ascii=False))
    
    elif command == 'task':
        account = sys.argv[2]
        title = sys.argv[3]
        due = sys.argv[4] if len(sys.argv) > 4 else None
        notes = sys.argv[5] if len(sys.argv) > 5 else None
        
        task = create_task(account, title, due, notes)
        print(json.dumps(task, indent=2, ensure_ascii=False))
    
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)
