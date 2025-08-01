from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from lxml import etree
import config
from collections import defaultdict
import pandas as pd
from concurrent.futures import ProcessPoolExecutor,as_completed
from rich import print as rprint
from pathlib import Path
import os
from dotenv import load_dotenv
import time

def get_users(tag):
    options = Options()
    options.add_argument("--headless=new")
    driver = webdriver.Chrome(options=options)
    resdict = defaultdict(list)
    driver.get(f"https://www.yiqicai.com/ex/ssqex_{tag}")
    WebDriverWait(driver,60).until(EC.presence_of_element_located((By.XPATH,"//div[@class='exp-list']")))
    uids = [int(i.xpath("@href")[0].split(".")[0].split("_")[-1]) for i in etree.HTML(driver.page_source).xpath("//div[@class='exp-list']")[0].xpath("a[@href]")]
    resdict["tag"].append(tag)
    resdict["pageno"].append(0)
    resdict["userids"].append(uids)
    
    for p in range(1,75):
        time.sleep(1)
        WebDriverWait(driver,60).until(EC.presence_of_element_located((By.XPATH,"//div[@class='btn-item btn-next']")))
        driver.find_element(By.XPATH, "//div[@class='btn-item btn-next']").click()
        WebDriverWait(driver,60).until(EC.presence_of_element_located((By.XPATH,"//div[@class='exp-list']")))
        uids = [int(i.xpath("@href")[0].split(".")[0].split("_")[-1]) for i in etree.HTML(driver.page_source).xpath("//div[@class='exp-list']")[0].xpath("a[@href]")]
        resdict["tag"].append(tag)
        resdict["pageno"].append(p)
        resdict["userids"].append(uids)
        rprint({"pageno":p,"tag":tag})
    df = pd.DataFrame(resdict)
    return df
if __name__ == "__main__":
    load_dotenv()
    seqno = os.getenv("SEQNO")
    tags = [1025,1020,1012,1003,1002,1001,1106,1103,1202,1302,2005,2003,2105]
    schemas = [config.srschema25,config.srschema20,config.srschema12,config.srschema3,config.srschema2,config.srschema1,config.srschemak6,config.srschemak3,config.srschematop2,config.srschematail2,config.sbschema5,config.sbschema3,config.sbschemak5]
    tag_schema = {i:j for i,j in zip(tags,schemas)}
    futures = []
    with ProcessPoolExecutor(max_workers=13) as executor:
        for tag in tags:
            future= executor.submit(get_users,tag)
            futures.append(future)
        resdflist = []
        for future in as_completed(futures):
            res = future.result()
            resdflist.append(res)
    rdf = pd.concat(resdflist,axis=0)
    rdf["schema"] = rdf["tag"].map(tag_schema)
    directory = Path("data/ssq")
    directory.mkdir(parents=True,exist_ok=True)
    filename = directory.joinpath(f"ssq_pageno_users_{seqno}.csv")
    rdf.to_csv(filename,index=False)