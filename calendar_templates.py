#!/usr/bin/env python3
"""
予定テンプレート
よく使う予定をテンプレート化
"""

import sys
import os
import json
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from openclaw_helper import create_event
from openclaw_integration import notify_calendar_event

# テンプレート保存先
TEMPLATE_FILE = os.path.join(os.path.dirname(__file__), 'templates.json')


def load_templates() -> Dict[str, Dict[str, Any]]:
    """テンプレートを読み込む"""
    if os.path.exists(TEMPLATE_FILE):
        try:
            with open(TEMPLATE_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            pass
    
    # デフォルトテンプレート
    return {
        'A社MTG': {
            'title': 'A社 定例MTG',
            'duration_minutes': 60,
            'location': 'オンライン',
            'description': '議題:\n1. \n2. \n3. ',
            'account': 'crosslink'
        },
        'ラーニングMTG': {
            'title': 'ラーニング事業部MTG',
            'duration_minutes': 60,
            'location': 'Google Meet',
            'description': '',
            'account': 'crosslink'
        },
        '体験会': {
            'title': 'プログラミング体験会',
            'duration_minutes': 120,
            'location': '現地',
            'description': '準備物:\n- PC\n- 教材\n- 名刺',
            'account': 'programming_school'
        }
    }


def save_templates(templates: Dict[str, Dict[str, Any]]):
    """テンプレートを保存"""
    with open(TEMPLATE_FILE, 'w', encoding='utf-8') as f:
        json.dump(templates, f, indent=2, ensure_ascii=False)


def create_template(
    name: str,
    title: str,
    duration_minutes: int,
    account: str,
    location: Optional[str] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """
    テンプレートを作成
    
    Args:
        name: テンプレート名（短縮名）
        title: イベントのタイトル
        duration_minutes: 所要時間（分）
        account: アカウント名
        location: 場所（オプション）
        description: 説明（オプション）
    
    Returns:
        作成されたテンプレート
    """
    templates = load_templates()
    
    template = {
        'title': title,
        'duration_minutes': duration_minutes,
        'account': account
    }
    
    if location:
        template['location'] = location
    if description:
        template['description'] = description
    
    templates[name] = template
    save_templates(templates)
    
    return template


def create_event_from_template(
    template_name: str,
    start_time: str,
    title_override: Optional[str] = None,
    location_override: Optional[str] = None,
    description_override: Optional[str] = None
) -> Dict[str, Any]:
    """
    テンプレートからイベントを作成
    
    Args:
        template_name: テンプレート名
        start_time: 開始時刻（ISO 8601形式）
        title_override: タイトルを上書き（オプション）
        location_override: 場所を上書き（オプション）
        description_override: 説明を上書き（オプション）
    
    Returns:
        作成結果
    """
    templates = load_templates()
    
    if template_name not in templates:
        return {
            'success': False,
            'message': f'テンプレート「{template_name}」が見つかりません'
        }
    
    template = templates[template_name]
    
    # 終了時刻を計算
    start_dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
    end_dt = start_dt + timedelta(minutes=template['duration_minutes'])
    end_time = end_dt.strftime('%Y-%m-%dT%H:%M:%S+09:00')
    
    # オーバーライドを適用
    title = title_override or template['title']
    location = location_override or template.get('location')
    description = description_override or template.get('description')
    
    # イベント作成
    event = create_event(
        account=template['account'],
        title=title,
        start=start_time,
        end=end_time,
        location=location,
        description=description
    )
    
    # 通知送信
    notify_calendar_event(
        account=template['account'],
        title=title,
        start_time=start_time,
        end_time=end_time,
        event_link=event.get('htmlLink')
    )
    
    return {
        'success': True,
        'event': event,
        'template': template_name,
        'message': f"✅ テンプレート「{template_name}」から予定を作成しました\n\n"
                  f"タイトル: {title}\n"
                  f"日時: {start_time} - {end_time}\n"
                  f"所要時間: {template['duration_minutes']}分\n"
                  f"リンク: {event.get('htmlLink')}"
    }


def parse_template_request(text: str) -> Optional[Dict[str, Any]]:
    """
    自然言語からテンプレート使用リクエストをパース
    
    Args:
        text: 「明日14時にA社MTG」など
    
    Returns:
        {'template': '...', 'start_time': '...', ...} or None
    """
    import re
    
    templates = load_templates()
    
    # テンプレート名を検索
    template_name = None
    for name in templates.keys():
        if name in text or name.lower() in text.lower():
            template_name = name
            break
    
    if not template_name:
        return None
    
    # 時刻を抽出
    from calendar_tools import parse_datetime
    
    try:
        start_time = parse_datetime(text)
    except:
        return None
    
    return {
        'template': template_name,
        'start_time': start_time
    }


def list_templates_formatted() -> str:
    """テンプレート一覧を整形して返す"""
    templates = load_templates()
    
    if not templates:
        return "📋 登録されているテンプレートはありません"
    
    result = "📋 **予定テンプレート一覧**\n\n"
    
    for name, template in templates.items():
        account_name = 'クロスリンク' if template['account'] == 'crosslink' else 'プログラミングスクール'
        
        result += f"**{name}**\n"
        result += f"  タイトル: {template['title']}\n"
        result += f"  所要時間: {template['duration_minutes']}分\n"
        result += f"  アカウント: {account_name}\n"
        
        if template.get('location'):
            result += f"  場所: {template['location']}\n"
        
        result += "\n"
    
    return result


# CLI エントリーポイント
if __name__ == '__main__':
    import json
    
    if len(sys.argv) < 2:
        print("Usage: python calendar_templates.py <command> [args...]")
        print("Commands:")
        print("  list                                      - テンプレート一覧")
        print("  create <name> <title> <duration> <account> [location] [desc]  - テンプレート作成")
        print("  use <template> <start_time>               - テンプレートから予定作成")
        print("  from-text <text>                          - 自然言語で作成")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == 'list':
        print(list_templates_formatted())
    
    elif command == 'create':
        name = sys.argv[2]
        title = sys.argv[3]
        duration = int(sys.argv[4])
        account = sys.argv[5]
        location = sys.argv[6] if len(sys.argv) > 6 else None
        description = sys.argv[7] if len(sys.argv) > 7 else None
        
        template = create_template(name, title, duration, account, location, description)
        
        print(f"✅ テンプレート「{name}」を作成しました\n")
        print(json.dumps(template, indent=2, ensure_ascii=False))
    
    elif command == 'use':
        template_name = sys.argv[2]
        start_time = sys.argv[3]
        
        result = create_event_from_template(template_name, start_time)
        print(result['message'])
    
    elif command == 'from-text':
        text = ' '.join(sys.argv[2:])
        
        parsed = parse_template_request(text)
        
        if not parsed:
            print("⚠️ テンプレートが見つかりません")
            print("\n利用可能なテンプレート:")
            print(list_templates_formatted())
        else:
            result = create_event_from_template(
                parsed['template'],
                parsed['start_time']
            )
            print(result['message'])
    
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)
