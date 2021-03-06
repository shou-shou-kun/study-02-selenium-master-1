from itertools import count
import os
from selenium.webdriver import Chrome, ChromeOptions
from selenium.webdriver import Firefox
from selenium.webdriver.firefox.options import Options
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
import time
import datetime
import pandas as pd
from webdriver_manager.chrome import ChromeDriverManager

# 定数は大文字の変数名が一般的
# {}に変数名をセットすると、後でformatで置換可能
LOG_FILE_PATH = "logs/log_{datetime}.log"
# EXP_CSV_PATH="results/exp_list_{search_keyword}_{datetime}.csv"
log_file_path=LOG_FILE_PATH.format(datetime=datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S'))


def makedir_for_filepath(filepath: str):
    '''
    ファイルを格納するフォルダを作成する
    '''
    # exist_ok=Trueとすると、フォルダが存在してもエラーにならない
    os.makedirs(os.path.dirname(filepath), exist_ok=True)

def log(txt):
    '''
    ログファイルおよびコンソール出力
    (学習用に１から作成しているが、通常はloggingライブラリを推奨)
    '''
    now = datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
    logStr = '[%s: %s] %s' % ('log',now , txt)
    # ログ出力
    makedir_for_filepath(log_file_path)
    with open(log_file_path, 'a', encoding='utf-8_sig') as f:
        f.write(logStr + '\n')
    print(logStr)

# Chromeを起動する関数

def set_driver(driver_path, headless_flg):
    if "chrome" in driver_path:
          options = ChromeOptions()
    else:
      options = Options()

    # ヘッドレスモード（画面非表示モード）をの設定
    if headless_flg == True:
        options.add_argument('--headless')

    # 起動オプションの設定
    options.add_argument(
        '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36')
    # options.add_argument('log-level=3')
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--ignore-ssl-errors')
    options.add_argument('--incognito')          # シークレットモードの設定を付与

    # ChromeのWebDriverオブジェクトを作成する。
    if "chrome" in driver_path:
        return Chrome(executable_path=os.getcwd() + "/" + driver_path,options=options)
    else:
        return Firefox(executable_path=os.getcwd()  + "/" + driver_path,options=options)

def page_view(driver): 
    # ページ終了まで繰り返し取得
    # 検索結果の会社のデータをまるっと取得
    name_list = driver.find_elements(by=By.CSS_SELECTOR, value=".cassetteRecruit")
    
    # 空のDataFrame作成
    df = pd.DataFrame()

    # 1ページ分繰り返し
    # print(len(name_list))

    for name_list in name_list:
        
        name = name_list.find_element(by=By.CSS_SELECTOR, value=".cassetteRecruit__name").text
        copy = name_list.find_element(by=By.CSS_SELECTOR, value=".cassetteRecruit__copy").text
        
        print(name,copy)
        # DataFrameに対して辞書形式でデータを追加する
        df = df.append(
            {"会社名": name, 
            "コピー": copy,
            "項目C": ""}, 
            ignore_index=True)
        
    # csv出力
    df.to_csv('to_csv_out.csv', mode = 'a', header = False) 
          
# main処理
def main(): 
    
    # 何ページ目
    page = 0
    
    # search_keyword = "高収入"
    search_keyword = input("検索ワードを入力してください　")
    
    log("処理開始")
    log("検索キーワード:{}".format(search_keyword))
    # 検索件数
    # total_count = driver.find_elements_by_class_name("js__searchRecruit--count")
    # print('検索件数 ： ',total_count) 
    print('検索ワード : ',search_keyword) 
    
    # driverを起動
    
    # if os.name == 'nt': #Windows
    #     driver = set_driver("chromedriver.exe", False)
    # elif os.name == 'posix': #Mac
    #     driver = set_driver("chromedriver", False)
    
    # chrome　driverの自動読み込み 
    driver = webdriver.Chrome(ChromeDriverManager().install())
        
    # Webサイトを開く
    driver.get("https://tenshoku.mynavi.jp/")
    time.sleep(5)
    # ポップアップを閉じる
    driver.execute_script('document.querySelector(".karte-close").click()')
    time.sleep(5)
    # ポップアップを閉じる
    driver.execute_script('document.querySelector(".karte-close").click()')

    # 検索窓に入力
    driver.find_element_by_class_name(
        "topSearch__text").send_keys(search_keyword)
    # 検索ボタンクリック
    driver.find_element_by_class_name("topSearch__button").click()

           
    # ページの表示
    # ページ終了まで繰り返し取得
    while True:
        page += 1
        print (page,'ページ目')
        log("{}ページ目".format(page))
        page_view(driver)
        
        try:
            next_btn = driver.find_element_by_class_name('iconFont--arrowLeft')
            next_btn.click()
        except NoSuchElementException:
            driver.quit()
            break    
    
    log("処理完了")    
       

# 直接起動された場合はmain()を起動(モジュールとして呼び出された場合は起動しないようにするため)
if __name__ == "__main__":
    main()
    