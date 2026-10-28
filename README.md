# canvas-board

JSON で書いたボード（セクションと付箋）を、見るだけのキャンバスHTMLにする小さなツールです。Python 3 の標準ライブラリだけで動き、書き出した HTML は1ファイルで完結します（外部への通信なし）。

- ドラッグ・2本指スクロールで移動、ピンチ・⌘+ホイールで拡大縮小
- 付箋をクリックすると、右側のパネルに全文と項目（プロジェクト・期限・完了条件・URL）を表示
- 配置は中身に合わせて自動で決まる（座標は書かなくてよい）
- ライト / ダークモード対応。表示位置はブラウザに保存される

画面上で付箋を動かす・編集する機能はありません。変更は `board.json` を書き換えて作り直します。

## 使い方

```sh
python3 build-board.py examples/board.json   # examples/board.html ができる
python3 build-board.py                        # カレントディレクトリの board.json を読む
```

HTML は `board.json` と同じフォルダに `board.html` として書き出されます。`board.html#today` のように末尾にセクションの id を付けると、そのセクションを開きます。

## board.json の項目

```json
{
  "title": "ボード名",
  "updated": "2026-10-28",
  "sections": [{"id": "tasks", "name": "タスク", "note": "補足"}, {"id": "today", "name": "今日", "parent": "tasks"}],
  "items": [{"id": "t1", "section": "today", "text": "やること", "color": "green"}]
}
```

### sections

| 項目 | 内容 |
|---|---|
| `id` | 一意な id |
| `name` | 見出し |
| `parent` | 入れ子にするときの親セクションの id（省略で最上位） |
| `note` | 見出しの横に出す補足 |

並び順は配列の順です。最上位のセクションの子が「入れ子を持たないセクションだけ」のときは、同じ幅の列（カンバン）として並び、列の中の付箋は上から積まれます。

### items

| 項目 | 内容 |
|---|---|
| `id` | 一意な id |
| `section` | 置くセクションの id |
| `type` | `sticky`（既定）・`link`・`text`・`priority` |
| `text` | 付箋・テキストの本文。5行を超える分は付箋では切れ、クリックで全文が見える |
| `color` | `green` `yellow`（既定）`gray` `red` `orange` `blue` `pink` `purple` |
| `project` `due` `goal` | 付箋に出すタグ・期限・完了条件 |
| `title` `desc` `site` `url` | リンクカード用 |
| `size` `w` | `text` の文字サイズと幅 |

並び順は配列の順です（列の中では上ほど優先、などの使い方ができます）。id の重複や存在しないセクションの指定があると、書き出さずにエラーを表示します。
