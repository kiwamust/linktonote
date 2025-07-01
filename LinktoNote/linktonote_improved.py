import streamlit as st
import requests
from bs4 import BeautifulSoup
import tempfile
import os
import re
import zipfile
from io import BytesIO
from datetime import datetime
from urllib.parse import urlparse
import time

# Streamlitの設定
st.set_page_config(
    page_title="LinkToNote for Obsidian",
    page_icon="📝",
    layout="wide"
)

class Config:
    """LinkToNote設定クラス"""
    REQUEST_TIMEOUT = 10
    USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    DEFAULT_TAGS = ['webclip', 'linktonote']
    MAX_TITLE_LENGTH = 50
    MAX_DESCRIPTION_LENGTH = 200
    MAX_FILENAME_LENGTH = 30

def is_valid_url(url):
    """URLの妥当性をチェック"""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except Exception:
        return False

def clean_text(text, max_length=None):
    """テキストをクリーンアップ"""
    if not text:
        return ""
    
    text = text.strip()
    text = re.sub(r'\s+', ' ', text)
    
    if max_length and len(text) > max_length:
        text = text[:max_length] + "..."
    
    return text

def safe_get_content(element):
    """BeautifulSoup要素から安全にcontentを取得"""
    if element is None:
        return None
    try:
        return element.get('content', '')
    except:
        return None

def safe_get_text(element):
    """BeautifulSoup要素から安全にテキストを取得"""
    if element is None:
        return None
    try:
        return element.get_text()
    except:
        return str(element) if element else None

def get_preview_robust(url, timeout=None):
    """堅牢なプレビュー取得関数"""
    if timeout is None:
        timeout = Config.REQUEST_TIMEOUT
    
    try:
        headers = {'User-Agent': Config.USER_AGENT}
        response = requests.get(url, timeout=timeout, headers=headers)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # タイトル取得の優先順位
        title = url  # デフォルト値
        
        # OGタイトル
        og_title = soup.find('meta', property='og:title')
        og_title_content = safe_get_content(og_title)
        if og_title_content:
            title = og_title_content
        else:
            # Twitterタイトル
            twitter_title = soup.find('meta', {'name': 'twitter:title'})
            twitter_title_content = safe_get_content(twitter_title)
            if twitter_title_content:
                title = twitter_title_content
            else:
                # 通常のタイトルタグ
                title_tag = soup.find('title')
                title_text = safe_get_text(title_tag)
                if title_text:
                    title = title_text
                else:
                    # H1タグ
                    h1_tag = soup.find('h1')
                    h1_text = safe_get_text(h1_tag)
                    if h1_text:
                        title = h1_text
        
        # 説明取得の優先順位
        description = "説明なし"  # デフォルト値
        
        # OG説明
        og_desc = soup.find('meta', property='og:description')
        og_desc_content = safe_get_content(og_desc)
        if og_desc_content:
            description = og_desc_content
        else:
            # 通常のdescription
            desc_meta = soup.find('meta', {'name': 'description'})
            desc_content = safe_get_content(desc_meta)
            if desc_content:
                description = desc_content
            else:
                # Twitter説明
                twitter_desc = soup.find('meta', {'name': 'twitter:description'})
                twitter_desc_content = safe_get_content(twitter_desc)
                if twitter_desc_content:
                    description = twitter_desc_content
        
        # テキストをクリーンアップ
        title = clean_text(title, Config.MAX_TITLE_LENGTH)
        description = clean_text(description, Config.MAX_DESCRIPTION_LENGTH)
        
        return title, description
        
    except Exception as e:
        error_msg = f"取得エラー: {str(e)[:50]}"
        return url, error_msg

def generate_obsidian_filename(title, url):
    """Obsidian用のファイル名を生成"""
    date_prefix = datetime.now().strftime("%Y%m%d-")
    
    clean_title = re.sub(r'[\\/*?:"<>|]', "", title)
    clean_title = re.sub(r'\s+', '-', clean_title)
    clean_title = clean_title[:Config.MAX_FILENAME_LENGTH]
    
    try:
        domain = urlparse(url).netloc.replace('www.', '')
        domain = re.sub(r'[\\/*?:"<>|]', "", domain)
    except:
        domain = "unknown"
    
    return f"{date_prefix}{clean_title}-{domain}.md"

def generate_obsidian_markdown(title, url, description, note, tags=None, include_frontmatter=True):
    """Obsidian形式のMarkdownを生成"""
    content = ""
    
    # フロントマター追加
    if include_frontmatter:
        frontmatter = "---\n"
        frontmatter += f"title: \"{title}\"\n"
        frontmatter += f"url: {url}\n"
        frontmatter += f"created: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
        if tags:
            formatted_tags = [f'"{tag}"' for tag in tags]
            frontmatter += f"tags: [{', '.join(formatted_tags)}]\n"
        frontmatter += "---\n\n"
        content += frontmatter
    
    # メインコンテンツ
    content += f"# {title}\n\n"
    content += f"**URL**: [{url}]({url})\n\n"
    content += f"**説明**: {description}\n\n"
    
    if note:
        content += f"## メモ\n{note}\n\n"
    
    # タグ追加
    if tags:
        tag_line = " ".join([f"#{tag}" for tag in tags])
        content += f"\n{tag_line}\n"
    
    return content

def process_links_with_progress(urls):
    """プログレスバー付きでリンクを処理"""
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    results = []
    for i, url in enumerate(urls):
        status_text.text(f'処理中: {i+1}/{len(urls)} - {url[:50]}...')
        result = get_preview_robust(url)
        results.append(result)
        progress_bar.progress((i + 1) / len(urls))
        
        # レート制限対策
        time.sleep(0.1)
    
    status_text.text('✅ 完了!')
    return results

def main():
    st.title("📝 LinkToNote for Obsidian")
    st.markdown("大量のWebリンクをObsidian用Markdownに一括変換")
    
    # サイドバー設定
    with st.sidebar:
        st.header("⚙️ 設定")
        
        # タグ設定
        default_tags_str = ", ".join(Config.DEFAULT_TAGS)
        tags_input = st.text_input("デフォルトタグ (カンマ区切り)", default_tags_str)
        tags = [tag.strip() for tag in tags_input.split(',') if tag.strip()]
        
        # フロントマター設定
        include_frontmatter = st.checkbox("フロントマター追加", True)
        
        st.markdown("---")
        st.markdown("**💡 ヒント**")
        st.markdown("- 生成されたファイルをObsidianのvaultフォルダにコピーしてください")
        st.markdown("- フロントマターはObsidianのプロパティとして認識されます")
    
    # メイン処理エリア
    st.header("📋 リンク入力")
    
    urls_input = st.text_area(
        "リンクを改行で複数入力してください",
        height=200,
        placeholder="https://example1.com\nhttps://example2.com\nhttps://example3.com\n...",
        help="1行に1つのURLを入力してください"
    )
    
    # オプション設定
    col1, col2 = st.columns(2)
    with col1:
        remove_duplicates = st.checkbox("重複リンクを除去", value=True)
    with col2:
        validate_urls = st.checkbox("URLの妥当性チェック", value=True)
    
    if urls_input:
        # URL処理
        urls = [url.strip() for url in urls_input.splitlines() if url.strip()]
        
        if remove_duplicates:
            urls = list(dict.fromkeys(urls))  # 順序を保持して重複除去
        
        # URL検証
        if validate_urls:
            valid_urls = []
            invalid_urls = []
            
            for url in urls:
                if is_valid_url(url):
                    valid_urls.append(url)
                else:
                    invalid_urls.append(url)
            
            if invalid_urls:
                st.warning(f"⚠️ 無効なURL ({len(invalid_urls)}個): {', '.join(invalid_urls[:3])}{'...' if len(invalid_urls) > 3 else ''}")
            
            urls = valid_urls
        
        if urls:
            st.success(f"✅ 処理対象: {len(urls)}個のリンク")
            
            # 処理開始ボタン
            if st.button("🚀 一括処理開始", type="primary"):
                start_time = time.time()
                
                st.info("📝 リンク情報を取得中...")
                results = process_links_with_progress(urls)
                
                processing_time = time.time() - start_time
                
                # 結果表示
                st.header("📊 処理結果")
                st.success(f"⏱️ 処理時間: {processing_time:.2f}秒 ({processing_time/len(urls):.2f}秒/リンク)")
                
                # ファイル生成と表示
                file_paths = []
                
                for i, (url, (title, description)) in enumerate(zip(urls, results)):
                    link_tags = tags.copy()
                    
                    # エキスパンダーでコンパクト表示
                    with st.expander(f"📄 {title[:50]}{'...' if len(title) > 50 else ''}", expanded=False):
                        col1, col2 = st.columns([2, 1])
                        
                        with col1:
                            st.markdown(f"**URL**: {url}")
                            st.markdown(f"**説明**: {description}")
                        
                        with col2:
                            # 個別メモ入力
                            note = st.text_area(
                                "メモ",
                                key=f"note_{i}",
                                height=80,
                                placeholder="このリンクについてのメモ..."
                            )
                            
                            # 個別タグ追加
                            additional_tags = st.text_input(
                                "追加タグ",
                                key=f"tags_{i}",
                                placeholder="tag1, tag2"
                            )
                            
                            if additional_tags:
                                link_tags.extend([tag.strip() for tag in additional_tags.split(',') if tag.strip()])
                    
                    # Markdownファイル生成
                    markdown_content = generate_obsidian_markdown(
                        title, url, description, note, link_tags, include_frontmatter
                    )
                    
                    # ファイル保存
                    filename = generate_obsidian_filename(title, url)
                    file_path = os.path.join(tempfile.gettempdir(), filename)
                    
                    with open(file_path, "w", encoding="utf-8") as f:
                        f.write(markdown_content)
                    file_paths.append(file_path)
                
                # ダウンロードセクション
                st.header("💾 ダウンロード")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.subheader("個別ダウンロード")
                    for i, (title, file_path) in enumerate(zip([r[0] for r in results], file_paths)):
                        filename = os.path.basename(file_path)
                        with open(file_path, "rb") as file:
                            st.download_button(
                                f"📄 {title[:30]}{'...' if len(title) > 30 else ''}",
                                file,
                                file_name=filename,
                                mime="text/markdown",
                                key=f"download_{i}"
                            )
                
                with col2:
                    st.subheader("一括ダウンロード")
                    
                    # ZIP形式での一括ダウンロード
                    zip_buffer = BytesIO()
                    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
                        for file_path in file_paths:
                            filename = os.path.basename(file_path)
                            zip_file.write(file_path, arcname=filename)
                    zip_buffer.seek(0)
                    
                    zip_filename = f"LinkToNote_Obsidian_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
                    
                    st.download_button(
                        "📦 すべてのファイルをZIPでダウンロード",
                        zip_buffer,
                        file_name=zip_filename,
                        mime="application/zip"
                    )
                    
                    # 統計情報
                    st.markdown("---")
                    st.markdown("**📈 統計情報**")
                    st.markdown(f"- 処理したリンク数: {len(urls)}")
                    st.markdown(f"- 生成したファイル数: {len(file_paths)}")
                    st.markdown(f"- 平均処理時間: {processing_time/len(urls):.2f}秒/リンク")
        else:
            st.warning("有効なURLが見つかりません。")

if __name__ == "__main__":
    main()