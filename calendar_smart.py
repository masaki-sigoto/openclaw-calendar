#!/usr/bin/env python3
"""
スマート提案機能
空き時間提案、ダブルブッキング検出など
"""

import sys
import os
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from calendar_view import get_unified_calendar, find_free_slots


def suggest_meeting_times(
    duration_minutes: int = 60,
    days_ahead: int = 7,
    preferred_hours: Tuple[int, int] = (9, 18),
    max_suggestions: int = 5
) -> List[Dict[str, Any]]:
    """
    ミーティングに最適な時間を提案
    
    Args:
        duration_minutes: 必要な時間（分）
        days_ahead: 何日先まで検索するか
        preferred_hours: 希望時間帯（開始時, 終了時）
        max_suggestions: 最大提案数
    
    Returns:
        提案リスト
    """
    # 空き時間を検索
    free_slots = find_free_slots(
        days_ahead=days_ahead,
        slot_duration_minutes=duration_minutes,
        work_hours=preferred_hours
    )
    
    # 提案を作成
    suggestions = []
    for slot in free_slots[:max_suggestions]:
        suggestions.append({
            'date': slot['date'],
            'time': slot['time'],
            'start': slot['start'],
            'end': slot['end'],
            'duration': duration_minutes,
            'score': _calculate_slot_score(slot)
        })
    
    # スコアでソート
    suggestions.sort(key=lambda x: x['score'], reverse=True)
    
    return suggestions


def _calculate_slot_score(slot: Dict[str, Any]) -> float:
    """
    空き時間のスコアを計算（好ましさの指標）
    
    Args:
        slot: 空き時間情報
    
    Returns:
        スコア（0.0 ~ 1.0）
    """
    try:
        start_dt = datetime.fromisoformat(slot['start'])
        
        score = 1.0
        
        # 午前中は高スコア
        if 9 <= start_dt.hour < 12:
            score *= 1.2
        
        # 昼休み直後は低スコア
        if start_dt.hour == 13:
            score *= 0.8
        
        # 17時以降は低スコア
        if start_dt.hour >= 17:
            score *= 0.7
        
        # 金曜日は高スコア
        if start_dt.weekday() == 4:
            score *= 1.1
        
        # 月曜日は低スコア
        if start_dt.weekday() == 0:
            score *= 0.9
        
        return min(score, 1.0)
    except:
        return 0.5


def detect_conflicts(
    start_time: str,
    end_time: str,
    account: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    ダブルブッキングを検出
    
    Args:
        start_time: 開始時刻（ISO 8601形式）
        end_time: 終了時刻
        account: 特定のアカウントのみチェック（オプション）
    
    Returns:
        競合するイベントのリスト
    """
    # 全予定を取得
    all_events = get_unified_calendar(days_ahead=365)
    
    # 時刻をパース
    try:
        new_start = datetime.fromisoformat(start_time.replace('Z', '+00:00')).replace(tzinfo=None)
        new_end = datetime.fromisoformat(end_time.replace('Z', '+00:00')).replace(tzinfo=None)
    except:
        return []
    
    conflicts = []
    for event in all_events:
        # アカウント指定があればフィルタ
        if account and event['account'] != account:
            continue
        
        try:
            # イベントの時刻をパース
            event_start_str = event['start']
            event_end_str = event['end']
            
            if 'T' not in event_start_str:
                continue  # 終日イベントはスキップ
            
            event_start = datetime.fromisoformat(event_start_str.replace('Z', '+00:00')).replace(tzinfo=None)
            event_end = datetime.fromisoformat(event_end_str.replace('Z', '+00:00')).replace(tzinfo=None)
            
            # 重複チェック
            if not (new_end <= event_start or new_start >= event_end):
                conflicts.append(event)
        except:
            pass
    
    return conflicts


def optimize_schedule(days_ahead: int = 7) -> Dict[str, Any]:
    """
    スケジュールを最適化して提案
    
    Args:
        days_ahead: 何日先まで分析するか
    
    Returns:
        最適化提案
    """
    all_events = get_unified_calendar(days_ahead=days_ahead)
    
    analysis = {
        'total_events': len(all_events),
        'busiest_day': None,
        'quietest_day': None,
        'suggestions': []
    }
    
    # 日ごとのイベント数をカウント
    day_counts = {}
    for event in all_events:
        try:
            start = event['start']
            if 'T' in start:
                date = start[:10]
            else:
                date = start
            
            day_counts[date] = day_counts.get(date, 0) + 1
        except:
            pass
    
    if day_counts:
        # 最も忙しい日と空いている日
        busiest = max(day_counts.items(), key=lambda x: x[1])
        quietest = min(day_counts.items(), key=lambda x: x[1])
        
        analysis['busiest_day'] = {'date': busiest[0], 'count': busiest[1]}
        analysis['quietest_day'] = {'date': quietest[0], 'count': quietest[1]}
        
        # 提案
        if busiest[1] > 5:
            analysis['suggestions'].append(
                f"⚠️ {busiest[0]} は {busiest[1]} 件の予定があり、過密です。一部を移動できませんか？"
            )
        
        if quietest[1] < 2:
            analysis['suggestions'].append(
                f"💡 {quietest[0]} は {quietest[1]} 件と空いています。重要なタスクに時間を使えます。"
            )
    
    # 連続するミーティングの検出
    consecutive_meetings = _detect_consecutive_meetings(all_events)
    if consecutive_meetings:
        analysis['suggestions'].append(
            f"⚠️ 連続するミーティングが {len(consecutive_meetings)} 回あります。休憩時間を入れることをお勧めします。"
        )
    
    return analysis


def _detect_consecutive_meetings(events: List[Dict[str, Any]]) -> List[Tuple[str, str]]:
    """
    連続するミーティングを検出
    
    Args:
        events: イベントリスト
    
    Returns:
        連続するミーティングのペアリスト
    """
    consecutive = []
    
    # 時刻順にソート済みと仮定
    for i in range(len(events) - 1):
        try:
            current_end = events[i]['end']
            next_start = events[i + 1]['start']
            
            if 'T' not in current_end or 'T' not in next_start:
                continue
            
            current_end_dt = datetime.fromisoformat(current_end.replace('Z', '+00:00'))
            next_start_dt = datetime.fromisoformat(next_start.replace('Z', '+00:00'))
            
            # 間隔が15分以下なら連続と判定
            gap = (next_start_dt - current_end_dt).total_seconds() / 60
            if gap <= 15:
                consecutive.append((events[i]['title'], events[i + 1]['title']))
        except:
            pass
    
    return consecutive


def format_suggestions(suggestions: List[Dict[str, Any]]) -> str:
    """
    提案をフォーマット
    
    Args:
        suggestions: 提案リスト
    
    Returns:
        フォーマットされたテキスト
    """
    if not suggestions:
        return "💡 提案できる時間がありません"
    
    result = "💡 **おすすめの時間**\n\n"
    
    for i, suggestion in enumerate(suggestions, 1):
        result += f"{i}. **{suggestion['date']} {suggestion['time']}**\n"
        result += f"   （{suggestion['duration']}分）\n"
        
        # スコアが高い場合は強調
        if suggestion.get('score', 0) > 0.9:
            result += "   ⭐ 特におすすめ\n"
        
        result += "\n"
    
    return result


# CLI エントリーポイント
if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python calendar_smart.py <command> [args...]")
        print("Commands:")
        print("  suggest [duration] [days]  - ミーティング時間を提案（デフォルト: 60分, 7日）")
        print("  conflict <start> <end>     - ダブルブッキングをチェック")
        print("  optimize [days]            - スケジュールを分析・最適化")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == 'suggest':
        duration = int(sys.argv[2]) if len(sys.argv) > 2 else 60
        days = int(sys.argv[3]) if len(sys.argv) > 3 else 7
        
        suggestions = suggest_meeting_times(duration_minutes=duration, days_ahead=days)
        print(format_suggestions(suggestions))
    
    elif command == 'conflict':
        start = sys.argv[2]
        end = sys.argv[3]
        
        conflicts = detect_conflicts(start, end)
        
        if not conflicts:
            print("✅ ダブルブッキングはありません")
        else:
            print(f"⚠️ {len(conflicts)}件の競合があります\n")
            for conflict in conflicts:
                print(f"  - {conflict['title']}")
                print(f"    {conflict['start']} - {conflict['end']}")
                print(f"    ({conflict['account_name']})")
                print()
    
    elif command == 'optimize':
        days = int(sys.argv[2]) if len(sys.argv) > 2 else 7
        
        analysis = optimize_schedule(days_ahead=days)
        
        print(f"📊 **スケジュール分析（{days}日間）**\n")
        print(f"総イベント数: {analysis['total_events']}件\n")
        
        if analysis['busiest_day']:
            print(f"最も忙しい日: {analysis['busiest_day']['date']} ({analysis['busiest_day']['count']}件)")
        if analysis['quietest_day']:
            print(f"最も空いている日: {analysis['quietest_day']['date']} ({analysis['quietest_day']['count']}件)")
        
        if analysis['suggestions']:
            print("\n💡 **提案**\n")
            for suggestion in analysis['suggestions']:
                print(f"  {suggestion}")
    
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)
