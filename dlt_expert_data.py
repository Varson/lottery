import requests
from lxml import etree
from collections import defaultdict
import time
import pandas as pd
from concurrent.futures import ProcessPoolExecutor,as_completed
import config
from fake_useragent import UserAgent
import time
import random
from python_retry import retry


def get_urls(seqno):
    urls = []
    base_url = "https://www.yiqicai.com/ex/dltex/tjxq_39_{i}_{num}.html"
    for i in range(1,2000):
        url = base_url.format(i=i,num=seqno)
        urls.append(url)
    return urls

@retry(max_retries=5)
def get_data(seqno,urls):
    resdict = defaultdict(list)
    for url in urls:
        print(url)
        uid = url.split("_")[2]
        headers= {'User-Agent':str(UserAgent().chrome)}
        response = requests.get(url,headers=headers)
        if config.srschema25 not in response.text:
            print(f"-----{url} is empty.------")
            continue
        html = etree.HTML(response.text)
        for li in html.xpath("//ul[@class='liTable']/li"):
            resdict["schema"].append(li.xpath("div[1]")[0].text)
            resdict["username"].append(html.xpath("//div[@class='exp-name']")[0].text)
            resdict["latest10_hitcount"].append(html.xpath("//span[@class='exp-count-col'][1]/span")[0].text)
            resdict["highest_continous_hitcount"].append(html.xpath("//span[@class='exp-count-col'][2]/span")[0].text)
            resdict["seqno"].append(seqno)
            resdict["userid"].append(uid)
            ddlist = []
            for dd in li.xpath("div[2]")[0].xpath("div/em"):
                ddlist.append(dd.text.zfill(2))
            resdict["numbers"].append(",".join(ddlist))
    df = pd.DataFrame(resdict)
    return df

if __name__ == "__main__":
    futures = []
    seqno = 2025069
    urls = get_urls(seqno)
    
    with ProcessPoolExecutor(max_workers=8) as executor:
        for i in range(0,len(urls),100):
            turls = urls[i:i+100]
            future= executor.submit(get_data,seqno,turls)
            futures.append(future)
        resdflist = []
        for future in as_completed(futures):
            res = future.result()
            resdflist.append(res)
    rdf = pd.concat(resdflist,axis=0)
    rdf.to_excel(f"data/dlt/dlt_expert_{seqno}.xlsx",index=False)
    
