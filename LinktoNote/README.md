
# LinkToNote

**LinkToNote**は、複数のWebリンクを一括で管理し、それぞれに対してコメントやメモを記録できるアプリケーションです。各リンクのプレビュー情報（タイトル、説明）を取得し、メモ付きのMarkdownファイルをリンクごとに作成できます。また、すべてのMarkdownファイルをZIP形式で一括ダウンロードする機能も備えています。

### 特徴

- 複数リンクを一括入力してプレビュー表示
- 各リンクに対するメモ入力
- リンクごとにMarkdownファイルを生成
- すべてのMarkdownファイルをZIPで一括ダウンロード
- 各Markdownファイルの末尾に「linktonoteから作成」を自動追記

---

### デモ

以下は、LinkToNoteの使用例です。

1. リンクを改行で区切り、複数入力します。
2. 各リンクのプレビューとメモ入力欄が表示されます。
3. 個別のMarkdownファイルのダウンロード、またはZIP形式での一括ダウンロードが可能です。

---

### インストール

1. **リポジトリのクローン**  
   ```bash
   git clone https://github.com/yourusername/linktonote.git
   cd linktonote
   ```

2. **依存ライブラリのインストール**  
   ```bash
   pip install -r requirements.txt
   ```

3. **アプリの起動**  
   ```bash
   streamlit run linktonote.py
   ```

4. **ブラウザでアクセス**  
   Streamlitが起動し、ブラウザに自動的に表示されます。手動で開く場合は、`http://localhost:8501`にアクセスしてください。

---

### 使い方

1. **リンク入力**  
   改行区切りで複数のWebリンクをテキストエリアに入力し、「Enter」を押します。

2. **プレビューとメモ**  
   各リンクのタイトルと説明が表示されます。表示されたメモ入力欄に自由にコメントやメモを追加してください。

3. **Markdownファイルの生成**  
   - 各リンクに対して、個別にMarkdownファイルをダウンロードできます。
   - また、すべてのMarkdownファイルをZIP形式で一括ダウンロードすることも可能です。

4. **自動追記**  
   生成されるMarkdownファイルの末尾には、「linktonoteから作成」というテキストが自動で追記されます。

---

### 主な機能

- **複数リンクの一括入力**  
   複数のWebリンクを改行で区切って一括入力できます。各リンクごとにコメントを残しながら整理できます。

- **リンクプレビューの自動取得**  
   各リンクのタイトルと説明を自動で取得し、プレビューとして表示します。

- **Markdownファイル生成と一括ダウンロード**  
   各リンクのメモをMarkdownファイルとしてリンクごとに保存可能。また、複数ファイルをZIP形式で一括ダウンロードできます。

---

### 使用例

以下のリンクを入力例として使用できます：

```plaintext
https://news.ycombinator.com/news
https://strainer.jp/
https://note.com/nyappa/n/ne52260a24430
https://www.radicalxchange.org/media/blog/lets-use-new-forms-of-money-to-commit-to-our-communities/
https://github.com/ByteByteGoHq/system-design-101
```

---

### 開発に関するメモ

このプロジェクトでは、Streamlit、BeautifulSoup、Markdownify、zipfileなどのライブラリを使用しています。カスタマイズや機能追加が容易で、さまざまな情報管理プロジェクトに拡張可能です。

---

### ライセンス

このプロジェクトはMITライセンスの下で公開されています。

---

### 貢献

フィードバックや機能改善のアイデアがあれば、IssueやPull Requestを通して貢献してください。
