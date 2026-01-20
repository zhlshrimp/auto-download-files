import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
import os

# 配置
SOURCE_FILE = 'files/url.txt'  # 源文件路径
OUTPUT_FILE = 'files/valid_urls.txt'  # 输出文件路径
TIMEOUT = 10  # 超时时间（秒）
MAX_WORKERS = 30  # 线程数

def get_proxies():
    # GitHub Actions 运行在国外，通常不需要代理，但如果有需要可在此配置
    return None

def check_url(url):
    """检测 URL 是否可用"""
    url = url.strip()
    if not url or url.startswith('#'):
        return None
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        # 使用 GET 请求，部分订阅链接不支持 HEAD
        response = requests.get(url, headers=headers, timeout=TIMEOUT)
        
        # 只要状态码是 200，就认为可用
        if response.status_code == 200:
            print(f"[可用] {url}")
            return url
        else:
            print(f"[无效] {url} (Status: {response.status_code})")
            return None
    except Exception as e:
        print(f"[出错] {url} (Error: {e})")
        return None

def main():
    # 1. 读取源文件
    if not os.path.exists(SOURCE_FILE):
        print(f"错误: 找不到源文件 {SOURCE_FILE}")
        return

    with open(SOURCE_FILE, 'r', encoding='utf-8') as f:
        # 读取行，去空字符
        raw_urls = [line.strip() for line in f if line.strip()]

    # 2. 去重 (利用 set 特性)
    unique_urls = list(set(raw_urls))
    print(f"源链接数量: {len(raw_urls)}，去重后数量: {len(unique_urls)}")

    # 3. 多线程并发检测
    valid_urls = []
    print("开始并发检测...")
    
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {executor.submit(check_url, url): url for url in unique_urls}
        for future in as_completed(futures):
            result = future.result()
            if result:
                valid_urls.append(result)

    # 4. 结果排序并写入文件
    valid_urls.sort()
    
    # 确保输出目录存在
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        for url in valid_urls:
            f.write(url + '\n')

    print("-" * 30)
    print(f"处理完成！")
    print(f"原始链接: {len(unique_urls)}")
    print(f"可用链接: {len(valid_urls)}")
    print(f"结果已保存至: {OUTPUT_FILE}")

if __name__ == '__main__':
    main()
