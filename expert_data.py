from lxml import etree
from collections import defaultdict
import pandas as pd
from concurrent.futures import ProcessPoolExecutor
from fake_useragent import UserAgent
from python_retry import retry
import httpx
import asyncio
from rich import print as rprint
import math
from pathlib import Path
from datetime import datetime
from functools import partial






def get_urls(seqno,uids,ltype,typeno):
    urls = []
    base_url = "https://www.yiqicai.com/ex/{ltype}ex/tjxq_{typeno}_{i}_{num}.html"
    for i in uids:
        url = base_url.format(i=i,num=seqno,ltype=ltype,typeno=typeno)
        urls.append(url)
    return urls



@retry(max_retries=5)
async def get_user_data(async_client,url,seqno):
    rprint(url)
    uid = url.split("_")[2]
    resdict = defaultdict(list)
    headers= {'User-Agent':str(UserAgent().getBrowser("random"))}
    response = await async_client.get(url,headers=headers)
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
    return pd.DataFrame(resdict)

async def main(urls,seqno):
    
    async_client = httpx.AsyncClient(timeout=60)
    corutines = []
    for url in urls:
        corutines.append(get_user_data(async_client,url,seqno))
    results = await asyncio.gather(*corutines,return_exceptions=True)
    await async_client.aclose()
    return results

def task_run(urls,seqno):
    res = asyncio.run(main(urls,seqno))
    df = pd.concat(res,axis=0,ignore_index=True)
    return df




if __name__ == "__main__":
    start = datetime.now()
    print(start)
    ltype = "ssq"
    typeno_dict = {"dlt":39,"ssq":5}
    typeno = typeno_dict[ltype]
    seqno = 2025083
    n_workers = 2
    batches = 8
    uidf = pd.read_csv(f"uid_{ltype}.csv",header=0,dtype={"userid":int})
    uids = uidf["userid"].unique()
    urls = get_urls(seqno,uids,ltype,typeno)
    pool = ProcessPoolExecutor(n_workers)
    batch = math.ceil(1500 / batches)
    batch_urls = [urls[i*batch:(i+1)*batch]for i in range(batches)]
    task_run_partial = partial(task_run,seqno=seqno)
    futures = pool.map(task_run_partial,batch_urls)
    rdf = pd.concat(futures,axis=0)
    directory = Path(f"data/{ltype}")
    directory.mkdir(parents=True,exist_ok=True)
    filename = directory.joinpath(f"{ltype}_expert_{seqno}.csv")
    rdf.to_csv(filename,index=False)
    end = datetime.now()
    rprint(end)
    rprint((end-start).seconds)

        





    
    
