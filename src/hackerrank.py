#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
from bs4.element import NavigableString, Tag

from urllib import request

import json


class Hackerrank(object):
    def __init__(self):
        super().__init__()

        self.dashboard_url = 'https://www.hackerrank.com/dashboard/'
        self.main_url = 'https://www.hackerrank.com'

        # :langs is a dict of matching languages: their common name and program name | { 'C++' : 'c_cpp'}
        # :got_tasks is a dict for calculating assigned tasks | { 'C++' : 0, 'Java' : 3 }
        self.langs, self.got_tasks = self.get_langs()
        
        # :current_task_url is an url of the last received task
        self.current_task_url = None
    
    # ----------------------------
    #       Public methods
    # ----------------------------

    def get_langs(self):
        langs = {}
        got_tasks = {}

        soup = BeautifulSoup(self.__get_url(self.dashboard_url), 'lxml')
        langs_urls = soup.find_all('a', class_='track-link')

        for lang in langs_urls:
            name = lang.text
            href = lang.attrs['data-attr2']
            langs[str(name).lower()] = href
            got_tasks[str(name).lower()] = 0

        return langs, got_tasks

    def get_task(self, lang):
        name_task, difficulty_task, task = self.__get_task(lang)

        formatted_task = self.__get_formatted_task(task)
        self.got_tasks[lang] += 1

        return name_task, difficulty_task, self.current_task_url, formatted_task

    # ----------------------------
    #       Private methods
    # ----------------------------
    
    def __get_url(self, url):
        response = request.urlopen(url)
        return response.read()

    def __get_tasks_url(self, lang, offset, limit):
        task_url = 'https://www.hackerrank.com/rest/contests/master/tracks/{}/challenges?offset={}&limit={}&track_login=true'.format(
            lang, offset, limit)
        return task_url
    
    def __parse_task(self, task):
        result_task = []
        
        self.current_task_url = f'https://www.hackerrank.com/challenges/{task}/problem'
        formatted_url = self.__get_url(self.current_task_url)
        
        soup = BeautifulSoup(formatted_url, 'lxml')
        content = soup.find('div', class_='challenge-body-html')
        
        special_symbol = ''

        for i, child in enumerate(content.contents):
            result_task.append([])
            content_child = child.find_all(['p', 'ul', 'pre'])

            for _content_child in content_child:
                result_task[i].append('\n')
                if _content_child.name == 'ul':
                    special_symbol = '• '
                else:
                    special_symbol = ''
                
                for i_content in _content_child:
                    if type(i_content) == NavigableString:
                        result_task[i].append(i_content)
                    elif type(i_content) == Tag:
                        if i_content.name == 'strong':
                            result_task[i].append(f'*** {i_content.text} ***')
                        else:
                            result_task[i].append(f'{special_symbol}{i_content.text}')
                        
        return result_task

        langs = {}
        got_tasks = {}

        soup = BeautifulSoup(self.__get_url(self.dashboard_url), 'lxml')
        langs_urls = soup.find_all('a', class_='track-link')

        for lang in langs_urls:
            name = lang.text
            href = lang.attrs['data-attr2']
            langs[str(name).lower()] = href
            got_tasks[str(name).lower()] = 0

        return langs, got_tasks

    def __get_task(self, lang):
        task_url = self.__get_tasks_url(self.langs[lang],
                                         self.got_tasks[lang] + 1,
                                         self.got_tasks[lang] + 1)
        complete_tasks_url = self.__get_url(task_url)

        soup = BeautifulSoup(complete_tasks_url, 'lxml')
        data = json.loads(soup.find('body').text)

        index_task = self.got_tasks[lang]
        name_task = data['models'][index_task]['name']
        difficulty_task = data['models'][index_task]['difficulty_name']
        name_formatted_task = data['models'][index_task]['slug']

        return name_task, difficulty_task, self.__parse_task(name_formatted_task)

    def __get_formatted_task(self, task):
        line_task = [''.join(line) for line in task]
        return ''.join(line_task)
