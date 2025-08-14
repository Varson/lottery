from selenium import webdriver
from selenium.webdriver.common.by import By
from lxml import etree
import config
from collections import defaultdict
import pandas as pd
from concurrent.futures import ProcessPoolExecutor,as_completed
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pathlib import Path
import os
from dotenv import load_dotenv
import time
from rich import print as rprint



def get_users(tag):
    options = Options()
    options.add_argument("--headless=new")
    driver = webdriver.Chrome(options=options)
    resdict = defaultdict(list)
    driver.get(f"https://www.yiqicai.com/ex/dltex_{tag}")
    WebDriverWait(driver,60).until(EC.presence_of_element_located((By.XPATH,"//div[@class='exp-list']")))
    uids = [int(i.xpath("@href")[0].split(".")[0].split("_")[-1]) for i in etree.HTML(driver.page_source).xpath("//div[@class='exp-list']")[0].xpath("a[@href]")]
    resdict["tag"].append(tag)
    resdict["pageno"].append(0)
    resdict["userids"].append(uids)
    tuid = uids[0]
    for p in range(1,75):
        WebDriverWait(driver,60).until(EC.presence_of_element_located((By.XPATH,"//div[@class='btn-item btn-next']")))
        driver.find_element(By.XPATH, "//div[@class='btn-item btn-next']").click()
        WebDriverWait(driver,60).until(EC.presence_of_element_located((By.XPATH,"//div[@class='exp-list']")))
        while True:
            uids = [int(i.xpath("@href")[0].split(".")[0].split("_")[-1]) for i in etree.HTML(driver.page_source).xpath("//div[@class='exp-list']")[0].xpath("a[@href]")]
            if uids[0]!=tuid:
                tuid = uids[0]
                break
        resdict["tag"].append(tag)
        resdict["pageno"].append(p)
        resdict["userids"].append(uids)
        rprint(uids[:2],p)
    df = pd.DataFrame(resdict)
    return df
if __name__ == "__main__":
    load_dotenv()
    seqno = os.getenv("SEQNO")
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
    directory = Path("data/dlt")
    directory.mkdir(parents=True,exist_ok=True)
    filename = directory.joinpath(f"dlt_pageno_users_{seqno}.csv")
    rdf.to_csv(filename,index=False)