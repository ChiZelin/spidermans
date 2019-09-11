#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

from bs4 import BeautifulSoup
from operator import itemgetter
import datetime
import json
import requests
import time

def get_tags():
    html=requests.get("https://leetcode.com/problemset/all/")
    soup = BeautifulSoup(html.text, 'html.parser')
    tag_as = soup.find_all('a', attrs='btn btn-xs btn-default round-btn tags-btn sm-topic') # 存储形如 "/tag/array/" 字符串的列表
    tags = []
    for tag_a in tag_as:
        tag_path = tag_a.get('href')[5:-1]
        tag_name = tag_a.find('span', attrs='text-sm text-gray').text
        tags.append({'tagName' : tag_name.strip(), 'tagPath' : tag_path})
    return tags

def get_questions_title_slugs(tag):
    post_url = 'https://leetcode.com/graphql'
    payload_data = {"operationName":"getTopicTag","variables":{"slug":"" + tag + ""},"query":"query getTopicTag($slug: String!) {\n  topicTag(slug: $slug) {\n    name\n    translatedName\n    questions {\n      titleSlug\n      isPaidOnly\n    }\n    }\n  \n}\n"}
    payload_header = {
        'content-type': 'application/json'
    }
    response = requests.post(post_url, data=json.dumps(payload_data), headers=payload_header)
    dictdata = response.json()
    return dictdata['data']['topicTag']['questions']

def get_question_datas(title_slug):
    post_url = 'https://leetcode.com/graphql'
    payload_data = {
        'operationName': 'questionData',
        'query': "query questionData($titleSlug: String!) {  question(titleSlug: $titleSlug) {    questionFrontendId    title    titleSlug    difficulty    likes    dislikes    }}",
        'variables': {
            'titleSlug': title_slug,
        }
    }
    payload_header = {
        'content-type': 'application/json'
    }
    while True:
        try:
            response = requests.post(post_url, data=json.dumps(payload_data), headers=payload_header)
            if response.text.startswith("{\"data\":"):
                break
        except KeyboardInterrupt:
            raise
        except:
            pass
    dict_data = response.json()
    return dict_data['data']['question']

tags = get_tags()
ranking_list = []
ranking_list.append("# " + "Leetcode Questions Ranking List  ")
ranking_list.append("According to this list, we can see which topics are popular.  " )
ranking_list.append("Whether you are a student or an interviewer, you can refer to this list when choosing questions.  \n" )
ranking_list.append("Ranking by Net Profit (Likes - Dislikes).  " )
ranking_list.append("Grouping by topic.  ")
ranking_list.append("No payment questions.  ")
ranking_list.append("Generated by: [LeetCode Questions Spiderman](https://github.com/ChiZelin/spidermans/tree/master/leetcode-questions-spiderman)  ")
ranking_list.append("Generated time: " + datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S' + "  "))
ranking_list.append("***********************************************")
md_file=open('LeetcodeRankingListRankingByNetProfit.md', 'w')
for i in ranking_list:
    md_file.write(i)
    md_file.write("\n")
for tag in tags:
    ranking_list = []
    tag_name = tag['tagName']
    tag_path = tag['tagPath']
    ranking_list.append("## " + tag_name)
    ranking_list.append("| ID | Title | Net Profit | Likes | Dislikes | Difficulty |")
    ranking_list.append("| :-------- | :-------- | :-------- | :------- | :------- | :-------- |")
    questions_infos = []
    questions_title_slugs = get_questions_title_slugs(tag_path)
    print(tag_name)
    for title_slug_data in questions_title_slugs:
        is_paid_only = title_slug_data['isPaidOnly']
        if is_paid_only == False:
            title_slug = title_slug_data['titleSlug']
            question_info = get_question_datas(title_slug)
            question_info['netProfit'] = question_info['likes'] - question_info['dislikes']
            questions_infos.append(question_info)
            print(question_info)
    questions_infos.sort(key=itemgetter('netProfit'), reverse=True)
    for question_info in questions_infos:
        ranking_list.append("| " + question_info['questionFrontendId'] + " | [" + question_info['title'] + "](" + "https://leetcode.com/problems/" +
        question_info['titleSlug'] + "/) | " + str(question_info['netProfit']) + " | " + str(question_info['likes']) + " | " + str(question_info['dislikes']) + " | " + question_info['difficulty'])
    for i in ranking_list:
        md_file.write(i)
        md_file.write("\n")
md_file.close()
print("LeetcodeRankingListRankingByNetProfit.md is generated!")