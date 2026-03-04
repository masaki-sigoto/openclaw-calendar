# OpenClaw Google Calendar Integration

OpenClawで複数のGoogleアカウントのカレンダー・タスクを自然言語で管理するシステム。

## ✨ 主な機能

### 📅 基本機能
- **複数アカウント対応**: クロスリンク・プログラミングスクールなど、複数のGoogleアカウントを統合管理
- **自然言語入力**: 「明日14時にA社と打ち合わせ、1時間」→ 自動でカレンダー登録
- **アカウント自動判定**: キーワードから自動でアカウントを判定（A社→クロスリンク、ココグラム→プログラミングスクール）
- **確認フロー**: キーワード判定時は確認を取り、明示的指定時は即登録
- **通知機能**: iMessage + Chatwork に自動通知

### 🚀 高度な機能

#### 1. 統合カレンダー表示 (`calendar_view.py`)
- 両アカウントの予定を統合表示
- 今日・今週・リスト表示
- 空き時間検索

```bash
python calendar_view.py today      # 今日の予定
python calendar_view.py week       # 今週の予定
python calendar_view.py free 7     # 7日間の空き時間
```

#### 2. 予定の編集・削除 (`calendar_edit.py`)
- タイトル検索で予定を削除
- 時刻・場所・説明の編集

```bash
python calendar_edit.py search "MTG"         # 予定を検索
python calendar_edit.py delete "テスト会議"   # 予定を削除
python calendar_edit.py update "MTG" "start" "2026-03-06T15:00:00+09:00"  # 時刻変更
```

#### 3. 定期予定の管理 (`calendar_recurring.py`)
- 繰り返し予定の作成
- 「毎週水曜10時にチームMTG」
- 「毎月第1金曜にレポート提出」

```bash
python calendar_recurring.py from-text "毎週水曜10時にチームMTG、1時間"
```

#### 4. リマインダー機能 (`calendar_reminder.py`)
- 予定の事前通知
- 今日の予定サマリー送信

```bash
python calendar_reminder.py check 60  # 60分後までの予定をチェック
python calendar_reminder.py daily     # 今日の予定サマリー
```

#### 5. スマート提案 (`calendar_smart.py`)
- 空き時間を提案
- ダブルブッキング検出
- スケジュール最適化

```bash
python calendar_smart.py suggest 60 7        # 60分の空き時間を提案
python calendar_smart.py optimize 7          # スケジュールを分析
```

#### 6. Google Tasks 連携 (`calendar_tasks.py`)
- カレンダーとタスクを統合管理
- タスク実行時間を提案

```bash
python calendar_tasks.py unified            # タスク & カレンダー統合表示
python calendar_tasks.py suggest 7 60       # タスク実行時間を提案
```

#### 7. 予定のテンプレート (`calendar_templates.py`)
- よく使う予定をテンプレート化
- ワンコマンドで定型予定を作成

```bash
python calendar_templates.py list                      # テンプレート一覧
python calendar_templates.py use "A社MTG" "2026-03-05T14:00:00+09:00"  # テンプレート使用
```

### 🤖 カレンダー監視 (`calendar_monitor.py`)
- 30分ごとに新しいイベントを自動検出
- Googleカレンダーに直接追加された予定も通知
- 招待されたイベントも自動通知

## 🛠️ セットアップ

### 1. 依存パッケージのインストール

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Google Cloud プロジェクト設定

1. [Google Cloud Console](https://console.cloud.google.com/) でプロジェクトを作成
2. Google Calendar API と Google Tasks API を有効化
3. OAuth 2.0 クライアントIDを作成
4. `credentials.json` をダウンロードして配置

### 3. 初回認証

```bash
python server.py
> auth crosslink
> auth programming_school
```

### 4. 環境変数設定（オプション）

Chatwork通知を有効にする場合：

```bash
cp .env.example .env
# .env ファイルを編集
CHATWORK_API_TOKEN=your_token_here
CHATWORK_ROOM_ID=your_room_id_here
```

## 📖 使い方

### OpenClaw からの使用

OpenClawから自然言語で操作：

```
真熙さん: 「明日14時にA社と打ち合わせ、1時間」
OpenClaw: → カレンダーに登録 + 通知送信
```

### コマンドライン

```bash
# 基本操作
python calendar_tools.py add "明日14時にA社と打ち合わせ、1時間"
python calendar_view.py today
python calendar_edit.py delete "テスト会議"

# 高度な機能
python calendar_recurring.py from-text "毎週水曜10時にチームMTG、1時間"
python calendar_smart.py suggest 60 7
python calendar_tasks.py unified
python calendar_templates.py use "A社MTG" "2026-03-05T14:00:00+09:00"
```

## 🔧 カスタマイズ

### アカウント判定ルール

`openclaw_helper.py` の `determine_account()` 関数でキーワードを編集できます。

```python
crosslink_keywords = [
    'a社', 'b社', '営業', '商談', '提案',
    'ラーニング', 'seo', 'ブログ', '記事',
    'プロシーズ', 'サンヴァーテックス'
]

programming_keywords = [
    '体験会', 'ココグラム', '座席表', 'シフト',
    '名古屋', '関西', '東海', '一宮', '門真'
]
```

### テンプレート追加

```bash
python calendar_templates.py create "新テンプレート" "タイトル" 60 crosslink "場所" "説明"
```

## 🤝 貢献

プルリクエスト歓迎！

## 📝 ライセンス

MIT License

## 🙏 謝辞

- OpenClaw - https://openclaw.ai
- Google Calendar API - https://developers.google.com/calendar

---

**作成日**: 2026年3月4日
