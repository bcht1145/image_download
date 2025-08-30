from concurrent.futures import *
import requests
from lxml import etree
import logging
import time
import os

"""
是的，你没看错，我的练手项目我给开源了
这也就是我闲的没事搞得代码
你爱看看，反正也写的不好
2025/07/30
"""

loggingg = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO,format='%(asctime)s - %(levelname)s - %(message)s',filename='log.log',filemode='w')
loggingg.info('---程序运行---')
HEAD = {'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36 Edg/138.0.0.0'}
p404 = 0
nowflord = os.path.join(os.getcwd(),'images')
if not os.path.isdir(nowflord):
    os.mkdir(nowflord)

def image(i,c,r):
    print("线程号",c,'下载编号',r)
    pid = i.get("pid")
    urls = i.get("urls")
    urlss = urls.get("original")
    try:
        responses = requests.get(urlss,headers=HEAD)
    except:
        print(f'错误{c}……{r}号')
    else:
        print(f'获取{c}……{r}号')
        if responses.status_code == 200:
            image_data = responses.content
            with open(os.path.join(nowflord,str(pid)+".jpg"), "wb") as image_file:
                image_file.write(image_data)
                print(f"成功{c}……{r}号")
        elif responses.status_code == 429:
            vs=1
            while True:
                print('请求数量过多，等待三十秒')
                for _ in range(30):
                    time.sleep(1)
                    print(f'下载编号{r}线程{c}剩余{30-_}秒')
                print(f'下载编号{r}线程{c}进行尝试第{vs}次')
                vs+=1
                try:
                    responses = requests.get(urlss,timeout=30)
                except:
                    pass
                if responses.status_code == 200:
                    image_data = responses.content
                    with open(os.path.join(nowflord,str(pid)+".jpg"), "wb") as image_file:
                        image_file.write(image_data)
                        print("成功……")
                    break
                elif responses.status_code == 429:
                    print("仍超时，将继续请求……")
                elif responses.status_code == 404:
                    print("请求错误！")
                    loggingg.warning(f'错误代码：'+str(responses.status_code))
                    loggingg.debug(urlss)
                    break
                else:
                    print("未知错误！")
                    loggingg.warning(f'错误代码：'+str(responses.status_code))
                    loggingg.debug(urlss)
                    break
        elif responses.status_code == 404:
            p404 += 1
            print("请求错误！")
            loggingg.warning(f'错误代码：'+str(responses.status_code))
            loggingg.debug(urlss)
        else:
            print("请求错误！")
            loggingg.warning(f'错误代码：'+str(responses.status_code))
            loggingg.debug(urlss)
def reque(x):
    url = "https://api.lolicon.app/setu/v2"
    data = {
        "r18":0,
        "num":20,
        "tag":[['']],
        "size":["original"]
    }
    r=0
    v=0
    n=0
    print("请求……")
    while True:
        response = requests.post(url, json=data,headers=HEAD)
        if response.status_code == 429:
            print("请求数量过多，将等待30秒后重试")
            for _ in range(30):
                time.sleep(1)
                print(f"还需等待{30-_}秒,线程号{x}")
        else:
            break
        print("等待完成，将继续尝试请求……")
    print("成功……")
    logging.info(f'请求第{x}次')
    json_data = response.json()
    # pid = json_data.get("pid")
    json_data_2 = json_data.get("data")
    v+=1
    with ThreadPoolExecutor(max_workers=128) as executor:
        # 提交多个任务，并为每个任务传递不同的参数
        futures = []
        for i in json_data_2:
            future = executor.submit(image,i,x,r)  # 将不同的参数 i 提交给 task
            futures.append(future)
            r+=1
            # 等待所有任务完成
        for future in as_completed(futures):
            try:
                future.result(timeout=300)  # 阻塞，直到任务完成
            except TimeoutError:
                print('任务超时……')
x = int(input("次数(次数*20为下载的数量)："))
print('将下载'+str(20*x)+'张')
loggingg.info(f'用户输入：{x}')
print("对目标网址的检查……")
vs = 1
while True:
    responese = requests.get(url='https://api.lolicon.app/setu/v2',headers=HEAD)
    if responese.status_code == 429:
        print("请求数量过多，将等待30秒后重试")
        for _ in range(30):
            time.sleep(1)
            print(f"还需等待{30-_}秒,已尝试{vs}次")
        vs+=1
    elif responese.status_code == 200:
        print("目标网址正确响应，正在获取……")
        break
    else:
        print(f'错误码为{responese.status_code}，无法处理，已结束')
        exit()
    print("等待完成，将继续进行检查……")
sttime = time.time()
with ThreadPoolExecutor(max_workers=5) as les:
    futer = []
    for i in range(x):
        fut = les.submit(reque,i)
        futer.append(fut)
        time.sleep(5)
    for fut in futer:
        fut.result()

loggingg.info('---程序结束---')
entime = time.time()
print("用时：",entime-sttime)
print(f'一共404了{p404}张')


