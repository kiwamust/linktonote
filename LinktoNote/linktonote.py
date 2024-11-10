import streamlit as st
import requests
from bs4 import BeautifulSoup
import tempfile
import os
import re
import zipfile
from io import BytesIO
from markdownify import markdownify as md

# Webページのプレビュー情報を取得する関数
def get_preview(url):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # タイトル取得
        title = soup.find('meta', property='og:title') or soup.find('title')
        title = title['content'] if title and title.has_attr('content') else title.text if title else url
        
        # ディスクリプション取得
        description = soup.find('meta', property='og:description') or soup.find('meta', {'name': 'description'})
        description = description['content'] if description else "プレビュー情報なし"

        return title, description
    except Exception as e:
        st.error(f"Failed to retrieve preview for {url}: {e}")
        return url, "プレビュー情報なし"

# ファイル名を生成する関数
def generate_filename(title_or_url):
    # タイトルまたはURLをベースにファイル名を作成し、無効な文字を除去
    safe_filename = re.sub(r'[\\/*?:"<>|]', "", title_or_url)[:50]  # 長すぎないよう50文字以内に制限
    return safe_filename + ".md"

# メインアプリケーション
st.title("LinkToNote")

# 複数リンクを改行で一括入力
urls_input = st.text_area("リンクを改行で複数入力してください", "")

# URLリストを取得し、セッション状態に保存
if "links" not in st.session_state:
    st.session_state.links = []
    st.session_state.notes = {}

if urls_input:
    urls = [url.strip() for url in urls_input.splitlines() if url.strip()]
    for url in urls:
        if url not in st.session_state.links:
            st.session_state.links.append(url)
            st.session_state.notes[url] = ""

# 各リンクに対してプレビューとメモ入力フィールドを表示
file_paths = []  # 各リンクのMarkdownファイルパスを格納するリスト
for link in st.session_state.links:
    st.subheader(f"リンク: {link}")
    title, description = get_preview(link)
    
    # タイトルと説明を表示
    st.markdown(f"**{title}**\n\n{description}")
    
    # コメント入力エリア
    note = st.text_area(f"気づきを記録してください ({link})", st.session_state.notes.get(link, ""))
    st.session_state.notes[link] = note

    # 個別のMarkdownファイル内容を生成
    markdown_content = f"- [{title}]({link})\n  - {note}\n\n"
    markdown_content += "\n#linktonote から作成"  # 追記部分

    file_name = generate_filename(title)  # 個別のファイル名を生成
    save_path = os.path.join(tempfile.gettempdir(), file_name)

    # 一時ファイルに保存し、パスをリストに追加
    with open(save_path, "w", encoding="utf-8") as f:
        f.write(markdown_content)
    file_paths.append(save_path)

    # 各リンクごとのダウンロードボタン
    with open(save_path, "rb") as file:
        st.download_button(f"{title} のMarkdownをダウンロード", file, file_name=file_name, mime="text/markdown")

# 複数ファイルをZIP形式で一括ダウンロード
if st.button("すべてのMarkdownファイルを一括ダウンロード"):
    # ZIPファイルのバッファを作成
    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, "w") as zip_file:
        for file_path in file_paths:
            file_name = os.path.basename(file_path)
            zip_file.write(file_path, arcname=file_name)
    zip_buffer.seek(0)

    # ZIPファイルのダウンロードボタン
    st.download_button("一括ダウンロード (ZIP形式)", zip_buffer, file_name="LinkToNote_Files.zip", mime="application/zip")