# Contributing to OpenClaw Google Calendar Integration

まず、このプロジェクトに興味を持っていただきありがとうございます！

## 💡 機能要望・バグ報告

[Issues](https://github.com/masaki-sigoto/openclaw-calendar/issues) から報告してください。

### バグ報告時に含めてほしい情報
- OS / Python バージョン
- 実行したコマンド
- エラーメッセージ（ full traceback）
- 再現手順

## 🛠️ 開発環境のセットアップ

```bash
# リポジトリをクローン
git clone https://github.com/masaki-sigoto/openclaw-calendar.git
cd openclaw-calendar

# 仮想環境を作成
python3 -m venv venv
source venv/bin/activate

# 依存パッケージをインストール
pip install -r requirements.txt

# Google Calendar API の認証
# credentials.json を配置してから
python server.py
> auth crosslink
```

## 📝 コーディング規約

- PEP 8 に従う
- 関数・クラスには docstring を書く
- 型ヒントを使う（Python 3.10+）
- コミットメッセージは日本語でOK

## 🔀 プルリクエストの流れ

1. このリポジトリをフォーク
2. 機能ブランチを作成 (`git checkout -b feature/amazing-feature`)
3. 変更をコミット (`git commit -m 'feat: すごい機能を追加'`)
4. ブランチにプッシュ (`git push origin feature/amazing-feature`)
5. プルリクエストを作成

### コミットメッセージの例

```
feat: 定期予定の管理機能を追加
fix: アカウント判定のバグを修正
docs: README にセットアップ手順を追加
refactor: calendar_tools.py を整理
```

## 🧪 テスト

新しい機能を追加した場合は、手動テストを実行してください：

```bash
# 基本機能のテスト
python calendar_tools.py add "テスト予定"
python calendar_view.py today
python calendar_edit.py search "テスト"

# 高度な機能のテスト
python calendar_recurring.py from-text "毎週水曜10時にテスト"
python calendar_smart.py suggest 60 7
python calendar_tasks.py unified
```

## 📚 ドキュメント

- コード内のコメント・docstring は日本語でOK
- README は日本語・英語どちらでもOK

## ❓ 質問

わからないことがあれば、[Discussions](https://github.com/masaki-sigoto/openclaw-calendar/discussions) で気軽に質問してください！

---

**Happy Hacking! 🎉**
