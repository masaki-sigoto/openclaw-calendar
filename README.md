# 🗓️ OpenClaw Google Calendar Integration

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![GitHub Stars](https://img.shields.io/github/stars/masaki-sigoto/openclaw-calendar?style=social)](https://github.com/masaki-sigoto/openclaw-calendar)

OpenClawで複数のGoogleアカウントのカレンダー・タスクを**自然言語**で管理するシステム。

> 💬 「明日14時にA社と打ち合わせ、1時間」  
> 🤖 → 自動でカレンダー登録 + 通知送信 🎉

---

## 📸 デモ

```
👤 「明日10時にチームMTG、1時間」

🤖 カレンダーに登録しました！
   📅 2026-03-05 10:00-11:00
   📍 アカウント: クロスリンク
   🔔 通知: iMessage + Chatwork
   🔗 https://calendar.google.com/...
```

---

## ✨ 主な機能

### 📅 基本機能
| 機能 | 説明 |
|------|------|
| 🌐 **複数アカウント対応** | 仕事用・個人用など複数のGoogleアカウントを統合管理 |
| 💬 **自然言語入力** | 「明日14時にMTG、1時間」で自動登録（AIパーサー内蔵） |
| 🎯 **アカウント自動判定** | キーワードから自動でアカウントを判定（「A社」→ 仕事用） |
| ✅ **確認フロー** | 自動判定時は確認、明示的指定時は即登録 |
| 🔔 **通知機能** | iMessage + Chatwork に自動通知 |
| 👀 **カレンダー監視** | 新しいイベントを30分ごとに自動検出して通知 |

### 🚀 高度な機能
| 機能 | 説明 |
|------|------|
| 📊 **統合カレンダー表示** | 複数アカウントの予定を統合表示、空き時間検索 |
| ✏️ **予定の編集・削除** | タイトル検索で簡単に編集・削除 |
| 🔄 **定期予定の管理** | 「毎週水曜10時にMTG」で繰り返し予定を作成 |
| ⏰ **リマインダー機能** | 予定の事前通知、今日の予定サマリー |
| 🧠 **スマート提案** | 空き時間提案、ダブルブッキング検出、スケジュール最適化 |
| ✅ **Google Tasks 連携** | カレンダーとタスクを統合管理 |
| 📋 **予定のテンプレート** | よく使う予定をワンコマンドで作成 |

---

## 🚀 クイックスタート

### 前提条件
- Python 3.10以上
- macOS（iMessage通知を使う場合）
- Google Cloud アカウント

### 1. インストール

```bash
git clone https://github.com/masaki-sigoto/openclaw-calendar.git
cd openclaw-calendar
./setup.sh
```

### 2. Google Cloud 設定

1. [Google Cloud Console](https://console.cloud.google.com/) でプロジェクトを作成
2. **Google Calendar API** と **Google Tasks API** を有効化
3. **OAuth 2.0 クライアントID** を作成（デスクトップアプリ）
4. `credentials.json` をダウンロードしてプロジェクトルートに配置

詳細な手順: [Google Calendar API クイックスタート](https://developers.google.com/calendar/api/quickstart/python)

### 3. 認証

```bash
source venv/bin/activate
python server.py
> auth account1
> auth account2
```

初回認証時、ブラウザが開いてGoogleログインが求められます。

### 4. 環境変数設定（オプション）

```bash
cp .env.example .env
# .env を編集
CHATWORK_API_TOKEN=your_token_here
CHATWORK_ROOM_ID=your_room_id_here
IMESSAGE_RECIPIENT=受信者の名前
```

---

## 📖 使い方

### 🎯 OpenClaw からの使用

OpenClawに統合すれば、自然言語で予定を管理できます：

```
👤 「明日14時にA社と打ち合わせ、1時間」
🤖 カレンダーに登録しました！

👤 「来週の予定を見せて」
🤖 📅 来週の予定（5件）...

👤 「金曜日の空き時間は？」
🤖 💡 金曜日の空き時間：10:00-12:00、14:00-17:00
```

### 💻 コマンドライン

#### 予定を作成

```bash
# 自然言語で作成
python calendar_tools.py add "明日14時にMTG、1時間"

# 定期予定を作成
python calendar_recurring.py from-text "毎週水曜10時にチームMTG、1時間"

# テンプレートから作成
python calendar_templates.py use "定例MTG" "2026-03-05T14:00:00+09:00"
```

#### カレンダーを表示

```bash
# 今日の予定
python calendar_view.py today

# 今週の予定
python calendar_view.py week

# 空き時間を検索（次の7日間）
python calendar_view.py free 7
```

#### 予定を編集・削除

```bash
# 予定を検索
python calendar_edit.py search "MTG"

# 予定を削除
python calendar_edit.py delete "テスト会議"

# 時刻を変更
python calendar_edit.py update "MTG" "start" "2026-03-06T15:00:00+09:00"
```

#### スマート機能

```bash
# 60分の空き時間を提案（次の7日間）
python calendar_smart.py suggest 60 7

# スケジュールを分析・最適化
python calendar_smart.py optimize 7

# ダブルブッキングをチェック
python calendar_smart.py conflict "2026-03-05T14:00:00+09:00" "2026-03-05T15:00:00+09:00"
```

#### タスク管理

```bash
# タスク & カレンダー統合表示
python calendar_tasks.py unified

# タスク実行時間を提案
python calendar_tasks.py suggest 7 60
```

#### リマインダー

```bash
# 60分後までの予定をチェック
python calendar_reminder.py check 60

# 今日の予定サマリーを送信
python calendar_reminder.py daily
```

---

## 🏗️ アーキテクチャ

```
┌─────────────────────────────────────────────────────┐
│                     OpenClaw                        │
│              (自然言語インターフェース)                │
└─────────────────┬───────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────┐
│            openclaw_calendar (本プロジェクト)          │
│  ┌─────────────────────────────────────────────┐   │
│  │  calendar_tools.py (自然言語パーサー)         │   │
│  │  openclaw_helper.py (アカウント判定)          │   │
│  └─────────────────────────────────────────────┘   │
│                        │                             │
│       ┌────────────────┼────────────────┐           │
│       ▼                ▼                ▼           │
│  ┌─────────┐    ┌──────────┐    ┌──────────┐      │
│  │ View    │    │ Edit     │    │ Smart    │      │
│  │ 表示     │    │ 編集     │    │ 提案     │      │
│  └─────────┘    └──────────┘    └──────────┘      │
│                        │                             │
│                        ▼                             │
│  ┌──────────────────────────────────────────┐      │
│  │     server.py (Google Calendar MCP)      │      │
│  │     OAuth認証 + API操作                   │      │
│  └──────────────────────────────────────────┘      │
└───────────────┬───────────────────┬─────────────────┘
                │                   │
                ▼                   ▼
      ┌─────────────────┐   ┌──────────────┐
      │  Google Calendar │   │ Google Tasks │
      │       API        │   │     API      │
      └─────────────────┘   └──────────────┘
                │
                ▼
      ┌─────────────────────────────┐
      │  通知 (iMessage + Chatwork)  │
      └─────────────────────────────┘
```

---

## 🔧 カスタマイズ

### アカウント判定ルール

`openclaw_helper.py` の `determine_account()` 関数でキーワードを編集：

```python
account1_keywords = [
    'a社', 'b社', '営業', '商談', '提案',
    'ラーニング', 'seo', 'ブログ'
]

account2_keywords = [
    '体験会', 'ココグラム', '座席表', 'シフト',
    '名古屋', '関西', '東海'
]
```

### テンプレート追加

```bash
python calendar_templates.py create "定例MTG" "週次定例MTG" 60 account1 "オンライン" "議題: TBD"
```

### カレンダー監視の設定

`HEARTBEAT.md` を編集して、監視間隔や動作をカスタマイズできます。

---

## 📁 ファイル構成

```
openclaw-calendar/
├── server.py                    # メインサーバー（OAuth認証、API操作）
├── calendar_tools.py            # 自然言語パーサー、イベント作成
├── calendar_view.py             # 統合カレンダー表示、空き時間検索
├── calendar_edit.py             # 予定の編集・削除
├── calendar_recurring.py        # 定期予定の管理
├── calendar_reminder.py         # リマインダー機能
├── calendar_smart.py            # スマート提案
├── calendar_tasks.py            # Google Tasks 連携
├── calendar_templates.py        # 予定のテンプレート
├── calendar_monitor.py          # カレンダー監視
├── openclaw_helper.py           # ヘルパー関数（アカウント判定）
├── openclaw_integration.py      # OpenClaw統合（通知）
├── notifications.py             # 通知サービス
├── gcal_cli.py                  # CLI ツール
├── requirements.txt             # 依存パッケージ
├── setup.sh                     # セットアップスクリプト
├── .env.example                 # 環境変数テンプレート
├── credentials.json.example     # OAuth認証情報テンプレート
├── README.md                    # このファイル
├── README_FULL.md               # 詳細ドキュメント
├── USAGE.md                     # 使い方ガイド
├── CHANGELOG.md                 # 変更履歴
├── CONTRIBUTING.md              # 貢献ガイド
└── LICENSE                      # MITライセンス
```

---

## ❓ FAQ / トラブルシューティング

### Q: 認証エラーが出ます

**A:** 以下を確認してください：
1. `credentials.json` が正しい場所にあるか
2. Google Cloud Console で Calendar API と Tasks API が有効になっているか
3. OAuth 2.0 クライアントIDが「デスクトップアプリ」として作成されているか

```bash
# トークンをリセット
rm token_*.json
python server.py
> auth account1
```

### Q: iMessage通知が送信されません

**A:** macOSのセキュリティ設定を確認してください：
1. システム設定 → プライバシーとセキュリティ → フルディスクアクセス
2. Terminalを追加
3. Terminalを再起動

### Q: 「毎週水曜」の定期予定が作成できません

**A:** v1.0.0でパーサーバグを修正しました。最新版を使用してください：

```bash
git pull origin main
python calendar_recurring.py from-text "毎週水曜10時にMTG、1時間"
```

### Q: 複数アカウントで同じアカウントが選ばれます

**A:** キーワードが重複している可能性があります。`openclaw_helper.py` のキーワードを確認してください：

```bash
grep -A10 "determine_account" openclaw_helper.py
```

### Q: Chatwork通知が送信されません

**A:** `.env` ファイルを確認してください：

```bash
cat .env
# CHATWORK_API_TOKEN が設定されているか確認
# CHATWORK_ROOM_ID が正しいか確認
```

---

## 🗺️ ロードマップ

### v1.1（予定）
- [ ] **Web UI** - ブラウザから予定を管理
- [ ] **Slack通知** - Chatworkに加えてSlack対応
- [ ] **Discord通知** - Discordサーバーに通知
- [ ] **音声入力** - Siri shortcutsで音声から予定作成
- [ ] **テストスイート** - 自動テストの追加

### v1.2（予定）
- [ ] **カレンダービュー画像生成** - 予定を画像として生成
- [ ] **DASH統合** - タスク管理システムとの深い統合
- [ ] **AIレコメンデーション** - 過去のパターンから予定を提案
- [ ] **多言語対応** - 英語・日本語以外の言語対応

### v2.0（将来）
- [ ] **モバイルアプリ** - iOS/Androidアプリ
- [ ] **チーム機能** - 複数人での予定共有
- [ ] **高度な分析** - 生産性レポート、時間分析

---

## 📚 詳細ドキュメント

- [📖 詳細な使い方](README_FULL.md)
- [📝 Changelog](CHANGELOG.md)
- [🤝 Contributing](CONTRIBUTING.md)
- [🛠️ SKILL.md](SKILL.md) - OpenClawスキルとしての使い方

---

## 🤝 貢献

プルリクエスト歓迎！詳細は [CONTRIBUTING.md](CONTRIBUTING.md) を参照してください。

バグ報告・機能要望は [Issues](https://github.com/masaki-sigoto/openclaw-calendar/issues) からお願いします。

---

## 📝 ライセンス

MIT License - 詳細は [LICENSE](LICENSE) を参照してください。

---

## 🙏 謝辞

- [OpenClaw](https://openclaw.ai) - AIアシスタントフレームワーク
- [Google Calendar API](https://developers.google.com/calendar)
- [Google Tasks API](https://developers.google.com/tasks)
- [Chatwork API](https://developer.chatwork.com/)

---

## 📞 コンタクト

- GitHub Issues: [openclaw-calendar/issues](https://github.com/masaki-sigoto/openclaw-calendar/issues)
- GitHub Discussions: [openclaw-calendar/discussions](https://github.com/masaki-sigoto/openclaw-calendar/discussions)

---

**作成日**: 2026年3月4日  
**最終更新**: 2026年3月4日

🌟 **Star** をつけてくれると嬉しいです！

---

Made with ❤️ for OpenClaw users
