# Google Calendar MCP Skill

複数のGoogleアカウントのカレンダー・タスクを管理するスキル。

## 機能

- 複数Googleアカウントの管理（クロスリンク・プログラミングスクール）
- カレンダーイベントの作成・取得
- Google Tasksのタスク作成・取得
- AI による自動アカウント振り分け
- カレンダー登録時の自動通知（Chatwork）

## 使い方

### 認証（初回のみ）

```bash
cd /Users/apple/.openclaw/workspace/google-calendar-mcp
source venv/bin/activate
python3 -c "from server import GoogleCalendarMCP; mcp = GoogleCalendarMCP(); mcp.authenticate('crosslink')"
python3 -c "from server import GoogleCalendarMCP; mcp = GoogleCalendarMCP(); mcp.authenticate('programming_school')"
```

### カレンダーイベントの作成

```python
from server import GoogleCalendarMCP

mcp = GoogleCalendarMCP()
mcp.authenticate('crosslink')
event = mcp.create_event(
    account='crosslink',
    summary='A社 定例MTG',
    start_time='2026-03-05T14:00:00+09:00',
    end_time='2026-03-05T15:00:00+09:00',
    description='議題: 新規提案について',
    location='オンライン'
)
print(f"✅ イベント作成: {event['htmlLink']}")
```

### カレンダーイベントの一覧

```python
from server import GoogleCalendarMCP

mcp = GoogleCalendarMCP()
mcp.authenticate('crosslink')
events = mcp.list_events('crosslink')
for event in events:
    start = event['start'].get('dateTime', event['start'].get('date'))
    print(f"{start}: {event['summary']}")
```

## OpenClaw からの使用

OpenClaw から Python コードを実行して使う：

```python
import sys
sys.path.insert(0, '/Users/apple/.openclaw/workspace/google-calendar-mcp')
from server import GoogleCalendarMCP

mcp = GoogleCalendarMCP()
# 認証情報は既に保存されているので、自動読み込み
mcp.authenticate('crosslink')

# イベント作成
event = mcp.create_event(
    account='crosslink',
    summary='テストイベント',
    start_time='2026-03-06T10:00:00+09:00',
    end_time='2026-03-06T11:00:00+09:00'
)
```

## アカウント振り分けルール

OpenClaw が自然言語から判断：

- **アカウント1**（例: work@company.com）
  - キーワード: A社、B社、営業、商談、提案、ラーニング、SEO、ブログ
  
- **アカウント2**（例: personal@gmail.com）
  - キーワード: 体験会、ココグラム、座席表、シフト、名古屋校、関西、東海

## 環境変数

Chatwork通知を有効にする場合：

```bash
# .env ファイルに追加
CHATWORK_API_TOKEN=your_token_here
CHATWORK_ROOM_ID=your_room_id_here
```

## トラブルシューティング

### 認証エラー

トークンファイルを削除して再認証：

```bash
cd /Users/apple/.openclaw/workspace/google-calendar-mcp
rm token_crosslink.json token_programming_school.json
```

### Python環境

仮想環境を使用：

```bash
cd /Users/apple/.openclaw/workspace/google-calendar-mcp
source venv/bin/activate
```
