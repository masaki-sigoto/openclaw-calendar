# 使い方ガイド

## OpenClaw から使う

### 1. Python から直接呼び出し

```python
import sys
sys.path.insert(0, '/Users/apple/.openclaw/workspace/google-calendar-mcp')
from calendar_tools import add_calendar_event_from_text, get_upcoming_events

# 自然言語でイベント作成
result = add_calendar_event_from_text('明日14時にA社と打ち合わせ、1時間')
print(result['summary'])

# 予定一覧を取得
print(get_upcoming_events('crosslink', days=3))
```

### 2. コマンドラインから操作

```bash
cd /Users/apple/.openclaw/workspace/google-calendar-mcp
source venv/bin/activate

# 自然言語でイベント作成
python3 calendar_tools.py add "明日14時にA社と打ち合わせ、1時間"

# 予定一覧（クロスリンクのみ、7日間）
python3 calendar_tools.py list crosslink 7

# 両アカウントの予定（今日のみ）
python3 calendar_tools.py list 1
```

## 自然言語の例

### イベント作成

```python
# 明日の予定
add_calendar_event_from_text('明日14時にA社と打ち合わせ、1時間')
add_calendar_event_from_text('明日10時からプロシーズ定例会、90分')

# 来週の予定
add_calendar_event_from_text('来週水曜15時にサンヴァーテックス様MTG')

# 絶対日付
add_calendar_event_from_text('3/10 13時に営業会議、2時間')
```

### 対応している自然言語表現

| 種類 | 例 |
|------|-----|
| **日付** | 明日、今日、来週水曜、3/5 |
| **時刻** | 14時、10:00、午後2時 |
| **時間** | 1時間、90分、30min |
| **アカウント判定** | A社・ラーニング → crosslink<br>ココグラム・座席表 → programming_school |

## アカウント自動判定のキーワード

### アカウント1（例: work@company.com）

- A社、B社、営業、商談、提案
- ラーニング、SEO、ブログ、記事
- プロシーズ、サンヴァーテックス

### アカウント2（例: personal@gmail.com）

- 体験会、ココグラム、座席表、シフト
- 名古屋、関西、東海、一宮、門真
- プログラミング、スクール

## 通知機能

### Chatwork 通知を有効にする

```.env
CHATWORK_API_TOKEN=your_token_here
CHATWORK_ROOM_ID=your_room_id_here
```

イベント作成時に自動でChatworkに通知が送信されます：

```
📅 予定を登録しました

日時: 2026/03/05(Thu) 14:00-15:00
タイトル: A社 打ち合わせ
アカウント: クロスリンク
リンク: https://www.google.com/calendar/...
```

## トラブルシューティング

### 認証が必要な場合

```bash
cd /Users/apple/.openclaw/workspace/google-calendar-mcp
source venv/bin/activate
python3 server.py

# CLI で認証
> auth crosslink
> auth programming_school
```

### トークンをリセット

```bash
cd /Users/apple/.openclaw/workspace/google-calendar-mcp
rm token_*.json
```

## 開発者向け

### 低レベル API

```python
from openclaw_helper import create_event, list_events

# 直接 API を呼ぶ
event = create_event(
    account='crosslink',
    title='テストイベント',
    start='2026-03-05T14:00:00+09:00',
    end='2026-03-05T15:00:00+09:00',
    description='説明文',
    location='会議室A'
)

# イベント一覧
events = list_events('crosslink', days_ahead=7)
```

### カスタマイズ

- `calendar_tools.py` の `determine_account()` 関数でアカウント判定ロジックを変更可能
- `parse_datetime()` 関数で日時パースルールを追加可能
