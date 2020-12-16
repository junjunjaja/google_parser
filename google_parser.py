from urllib.request import Request, urlopen
from urllib.parse import quote_plus
from bs4 import BeautifulSoup
import pandas as pd
import re
import asyncio
import string
from time import time
from urllib.error import HTTPError

def str_clean(state):
    return state.translate(str.maketrans('', '', string.punctuation)).translate(str.maketrans('', '', string.digits)).replace(
        "  ", " ").strip()
def stop_words(state):
    stop_w = ["is","the","a","an","and","are","was","were","to","as","in","of","by","at"]
    comp = re.compile(r"\b|\b".join(stop_w))
    white = re.compile(r"\s{2,}")
    return white.sub(" ",comp.sub("",state)).strip()
async def main(urls,state,verbose =True,time_=False):
    if time_:
        s_t1 = time()
    c_state = str_clean(state)
    c_state = list(set(stop_words(c_state).split(" ")))
    futures = [asyncio.ensure_future(quilet_parse(url,c_state,time_)) for url in urls]
    result = await asyncio.gather(*futures)
    if time_:
        print("problem sol 얻어오는 시간",(time()-s_t1))
        s_t1 = time()
    df = pd.concat(result, axis=0)
    q_max = df[2].max()
    s_max = df[3].max()
    a_max = max(q_max,s_max)
    df = df[(df[2] == a_max) | (df[3] == a_max)][["prob", "sol"]]
    split_num = 130
    if time_:
        print("최종 DF 처리하는 시간", (time() - s_t1))
    if verbose:
        if q_max >= s_max:
            print()
            print()
            print("Problem 으로 찾음")
        if q_max < s_max:
            print()
            print()
            print("Solution 으로 찾음")

        for n,d in df.iterrows():
            print()
            print("Problem -------------------------------------------------")
            for i in d["prob"].split(". "):
                if len(i) < split_num:
                    print(i, end=".")
                    print()
                else:
                    for _ in range(split_num,len(i),split_num):
                        print(i[(_-split_num):_])
                    print(i[_:], end=".")
            print()
            print("Solution -------------------------------------------------")
            for i in d["sol"].split(". "):
                if len(i) < split_num:
                    print(i, end=".")
                    print()
                else:
                    for _ in range(split_num,len(i),split_num):
                        print(i[(_-split_num):_])
                    print(i[_:], end=".")
            print()
    return df

def prob_sol_df(bs,state):
    prob = []
    sol = []
    n = 0
    a_p = []
    a_s = []
    for i in bs.findAll('span', attrs={'class': 'TermText notranslate lang-en'}, recursive=True):
        if n % 2 == 0:
            a_p.append(word_count(state, str_clean(i.text)))
            prob.append(i.text)
        else:
            a_s.append(word_count(state, str_clean(i.text)))
            sol.append(i.text)
        n += 1
    df = pd.DataFrame([prob, sol, a_p, a_s]).T.rename(columns={0: "prob", 1: "sol"})
    return df
async def quilet_parse(url,state,time_):
    req = Request(url, headers={
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36',
        "lang": "ko_KR", "disable-gpu": True})
    if time_:
        s_t1 = time()
    try:
        response = await asyncio.get_event_loop().run_in_executor(None, urlopen, req)
    except HTTPError:
        return
    page = await asyncio.get_event_loop().run_in_executor(None, response.read)
    bs = await asyncio.get_event_loop().run_in_executor(None, BeautifulSoup,page, 'html.parser')
    df = await asyncio.get_event_loop().run_in_executor(None, prob_sol_df,bs,state)
    if time_:
        print("개별 parser 처리하는 시간", (time() - s_t1))
    return df[(df[2] ==df[2].max()) | (df[3] ==df[3].max())]


def word_count(state,qustion):
    return len([d for d in state if d in qustion])

def google_search(state,get_url = False,time_ = False):
    if time_:
        s_t1 = time()
    c_state = stop_words(str_clean(state))
    c_state = re.compile(r"\b\w{1}\b").sub("", c_state)
    c_state = re.compile(r"\s{2,}").sub(" ",c_state)
    baseUrl = 'https://www.google.com/search?q='
    plusUrl = "site:quizlet.com" +" "+ c_state
    url = baseUrl + quote_plus(plusUrl)
    req = Request(url, headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36',"lang":"ko_KR","disable-gpu":True})
    res = urlopen(req).read()
    bs = BeautifulSoup(res, 'html.parser')
    b = bs.findAll('a', recursive=True)
    links = []
    for b_ in b:
        try:
            if re.compile("^https://quizlet.com/").search(b_['href']) is not None:
                links.append(b_['href'])
        except:
            pass
    if time_:
        print("구글 링크 처리하는 시간", (time() - s_t1))
    if get_url:
        return links


if __name__ == "__main__":
    k = "a"
    state = None
    start = 0
    n = 6
    end = n
    google_pass = False
    verbose = True
    time_ = True
    while k != "q":
        if state is None:
            state = input("검색하고자하는 질문 입력하세요 : ")
        elif state == "need short":
            state = input("검색하고자하는 질문을 좀 더 짧게 입력하세요 : ")
        if not google_pass:
            links = google_search(state, get_url=True,time_ = time_)
        #print(links)
        if len(links) >=1:
            if len(links) > start:
                if len(links) > end:
                    asyncio.get_event_loop().run_until_complete(main(links[start:end], state,verbose,time_))
                else:
                    asyncio.get_event_loop().run_until_complete(main(links[start:], state,verbose,time_))
            else:
                asyncio.get_event_loop().run_until_complete(main(links, state,verbose,time_))
        else:
            state = "need short"
            continue
        k = input("Press q to quit 다른 결과는 else를 입력하세요 :")
        if k =="else":
            print()
            print("기존 질문과 같은 항목 검색")
            print()
            start += n
            end += n
            google_pass = True
            continue
        if len(k) >=10:
            state = k
            print()
            print(f"새로운 질문 {state[:20]} ~ 으로 검색")
            print()

        else:
            state = None
        start = 0
        end = n
        google_pass = False
