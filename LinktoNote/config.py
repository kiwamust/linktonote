class Config:
    """LinkToNote設定クラス"""
    REQUEST_TIMEOUT = 10
    MAX_CONCURRENT_REQUESTS = 5
    USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    DEFAULT_TAGS = ['webclip', 'linktonote']
    MAX_TITLE_LENGTH = 50
    MAX_DESCRIPTION_LENGTH = 200
    MAX_FILENAME_LENGTH = 30