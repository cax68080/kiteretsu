# 青空文庫からのダウンロード＆加工用共通コード
# 青空文庫からのダウンロードzip展開＆テキスト提出
import re
import traceback
import zipfile
import urllib.request
import os.path,glob

# 青空文庫のURLから小説テキストデータを得る関数
def get_flat_text_from_aozora(zip_url):
    import re as rr
    # zipファイル名の取得
    zip_file_name = rr.split(r'/',zip_url)[-1]
    print(zip_file_name)

    # すでにダウンロード済か確認後、URLからファイルを取得
    if not os.path.exists(zip_file_name):
        print('Download URL = ',zip_url)
        data = urllib.request.urlopen(zip_url).read()
        with open(zip_file_name,mode="wb") as f:
            f.write(data)
    else:
        print('May be already exists')

    # 拡張子を除いた名前で、展開用フォルダを作成
    dir,ext = os.path.splitext(zip_file_name)
    if not os.path.exists(dir):
        os.makedirs(dir)
    
    # zipファイルの中身をすべて、展開用フォルダに展開
    unzipped_data = zipfile.ZipFile(zip_file_name,'r')
    unzipped_data.extractall(dir)
    unzipped_data.close()

    # zipファイルの削除
    os.remove(zip_file_name)
    # 注：展開フォルダの削除は入れていない

    # テキストファイル(.txt)の抽出
    wild_path = os.path.join(dir,'*.txt')
    # テキストファイルは原則1つ同梱。最初の１つを取得
    txt_file_path = glob.glob(wild_path)[0]

    print(txt_file_path)
    # 青空文庫はshift_jisのためのでコードしてutf8にする
    binary_data = open(txt_file_path,'rb').read()
    main_txt = binary_data.decode('shift_jis')

    # 取得したutf8のテキストデータを返す
    return main_txt

# 青空文庫のデータを加工して扱いやすくするコード

# 外字データ変換のための準備
# 外字変換のための対応表(jisx0213対応表)のダウンロード
# ※事前にダウンロード済であれば飛ばしてよい
# wget http://x0213.org/codetable/jisx0213-2004-std.txt

import re

# 外字変換のための対応表(jisx0213対応表)の読み込み
with open('jisx0213-2004-std.txt') as f:
    ms = (re.match(r'(\d-\w{4})\s+U\+(\w{4,5})',l) for l in f if l[0] != '#')
    gaiji_table = {m[1]: chr(int(m[2],16)) for m in ms if m}

# 外字データの置き換えのための関数
def get_gaiji(s):
    # ※[＃ 「弓＋椋のつくり」、第3水準1-84-22]の形式を変換
    m = re.search(r'第(\d)水準\d-(\d{1,2})-(\d{1,2})',s)
    if m:
        key = f'{m[1]}-{int(m[2])+32:2X}{int(m[3])+32:2X}'
        return gaiji_table.get(key,s)
    # ※[＃ 「身＋箪」、U+8EC3、56-1]の形式を変換
    m = re.search(r'U\+(\w{4})',s)
    if m:
        return chr(int(m[1],16))
    # ※[＃二の字点、1-2-22]、[＃感嘆符二つ、1-8-75]の形式を変換
    m = re.search(r'.*?(\d)-(\d{1,2})-(\d{1,2})',s)
    if m:
        key = f'{int(m[1])+2}-{int(m[2])+32:2X}{int(m[3])+32:2X}'
        return gaiji_table.get(key,s)
    # 不明な形式の場合、元の文字列をそのまま返す
    return s
# 青空文庫の外字データ置き換え＆注釈＆ルビ除去などを行う加工関数
def flatten_aozora(text):
    # textの外字データ表記を漢字に置き換える処理
    text = re.sub(r'※[＃.+?]',lambda m: get_gaiji(m[0]),text)
    # 注釈文やルビなどの除去
    text = re.split(r'\-{5,}',text)[2]
    text = re.split(r'底本：',text)[0]
    text = re.sub(r'《.+?》','',text)
    text = re.sub(r'[＃.+?]','',text)
    text = text.strip()
    return text

# 複数ファイルのダウンロードや加工を一括実行する関数
import time
# ZIP-URLのリストからすべてのデータをダウンロード＆加工する関数
def get_all_flat_text_from_zip_list(zip_list):
    all_flat_text = ""
    for zip_url in zip_list:
        # ダウンロードや解凍の失敗があり得るためTry文を使う
        # 十分なデータ量があるため数件の失敗はスキップでよい
        try:
            # 青空文庫からダウンロードする関数を実行
            aozora_dl_text = get_flat_text_from_aozora(zip_url)
            # 青空文庫のテキストを加工する関数を実行
            flat_text = flatten_aozora(aozora_dl_text)
            # 結果を追記して改行
            all_flat_text += flat_text + ("\n")
            print(zip_url+"：取得＆加工完了")
        except:
            # エラー時の詳細ログを出すおまじない
            import traceback
            traceback.print_exc()
            print(zip_url+"：取得or解凍エラーのためスキップ")
            # 青空文庫サーバに負荷をかけすぎないように1秒待ってから次の小説へ
            time.sleep(1)
    # 全部がつながった大きなテキストデータを返す
    return all_flat_text

# ダウンロードしたいURLを入力する
#「走れメロス」
ZIP_URL = 'https://www.aozora.gr.jp/cards/000035/files/1567_ruby_4948.zip'

# 青空文庫からダウンロードする関数を実行
#aozota_dl_text = get_flat_text_from_aozora(ZIP_URL)
#print(aozota_dl_text)
        
