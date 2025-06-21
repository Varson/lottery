from selenium import webdriver
from selenium.webdriver.common.by import By
from lxml import etree
import config
from collections import defaultdict
import pandas as pd
import time
from concurrent.futures import ProcessPoolExecutor,as_completed
from selenium.webdriver.chrome.options import Options



def get_users(tag):
    chrome_options = Options()
    # chrome_options.add_argument("--headless")
    driver = webdriver.Chrome(options=chrome_options)
    time.sleep(5)
    resdict = defaultdict(list)
    driver.get(f"https://www.yiqicai.com/ex/dltex_{tag}")
    time.sleep(5)
    uids = [int(i.xpath("@href")[0].split(".")[0].split("_")[-1]) for i in etree.HTML(driver.page_source).xpath("//div[@class='exp-list']")[0].xpath("a[@href]")]
    resdict["tag"].append(tag)
    resdict["pageno"].append(0)
    resdict["userids"].append(uids)
    
    for p in range(1,75):
        driver.find_element(By.XPATH, "//div[@class='btn-item btn-next']").click()
        time.sleep(5)
        uids = [int(i.xpath("@href")[0].split(".")[0].split("_")[-1]) for i in etree.HTML(driver.page_source).xpath("//div[@class='exp-list']")[0].xpath("a[@href]")]
        resdict["tag"].append(tag)
        resdict["pageno"].append(p)
        resdict["userids"].append(uids)
    df = pd.DataFrame(resdict)
    return df
if __name__ == "__main__":
    seqno = 2025069
    tags = [1025,1020,1010,1003,1002,1001,1106,1103,2006,2002,2001,2103]
    schemas = [config.drschema25,config.drschema20,config.drschema10,config.drschema3,config.drschema2,config.drschema1,config.drschemak6,config.drschemak3,config.dbschema6,config.dbschema2,config.dbschema1,config.dbschemak3]
    tag_schema = {i:j for i,j in zip(tags,schemas)}
    futures = []
    with ProcessPoolExecutor(max_workers=12) as executor:
        for tag in tags:
            future= executor.submit(get_users,tag)
            futures.append(future)
        resdflist = []
        for future in as_completed(futures):
            res = future.result()
            resdflist.append(res)
    rdf = pd.concat(resdflist,axis=0)
    rdf["schema"] = rdf["tag"].map(tag_schema)
    rdf.to_csv(f"users/dlt/dlt_pageno_users_{seqno}.csv",index=False)