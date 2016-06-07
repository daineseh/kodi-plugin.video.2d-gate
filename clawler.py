# -*- coding: utf8 -*-

from bs4 import BeautifulSoup
from collections import OrderedDict

import requests
import urlparse


GOOGLE_URL = 'https://drive.google.com/file/d/'
BUILD_GOOGLE_URL = lambda x: urlparse.urljoin(GOOGLE_URL, x).encode('utf8')

BASE_URL = 'http://2d-gate.org'
BUILD_URL = lambda x: urlparse.urljoin(BASE_URL, x).encode('utf8')


class Episode:
    def __init__(self, name = None, url = None,
                 thumb = None, background = None):
        self.name = self._to_str_type(name)
        self.url = self._to_str_type(url)
        self.thumb = self._to_str_type(thumb)
        self.background = self._to_str_type(background)

    def _to_str_type(self, value):
        if not value:
            return
        if isinstance(value, str):
            return value
        return value.encode('utf8')

    @property
    def background(self):
        return self.__background

    @background.setter
    def background(self, value):
        self.__background = value

    @property
    def name(self):
        return self.__name

    @name.setter
    def name(self, value):
        self.__name = value

    @property
    def thumb(self):
        return self.__thumb

    @thumb.setter
    def thumb(self, value):
        self.__thumb = value

    @property
    def url(self):
        return self.__url

    @url.setter
    def url(self, value):
        self.__url = value


class ProcessEpisodes:
    def __init__(self, url):
        self.url = url
        self.req = requests.get(self.url)
        self.soup = BeautifulSoup(self.req.text, 'html.parser')
        self.episodes_list = []
        self.__parse()

    def __parse_tab(self, tag, prefix=None):
        tab_data = []
        div_tag = tag.find('div', {'style': 'display:none'})
        if not div_tag:
            return tab_data
        ul_tag = div_tag.find('ul')
        if not ul_tag:
            return tab_data

        for li_tag in ul_tag.find_all('li'):
            tag_a = li_tag.find('a')
            if not tag_a:
                continue
            tab_id = tag_a.get('href').split('#')[-1]
            if prefix:
                tab_name = prefix + '-' + tag_a.string
            else:
                tab_name = tag_a.string
            tab_data.append((tab_id, tab_name))
        return tab_data

    def __parse_info_style1(self, tag):
        span_tag = tag.find('span')
        if not span_tag:
            return None, None
        href = span_tag.get('href')
        if not href:
            return None, None
        # Workaround
        assert isinstance(href, str)
        if 'amp;' in href:
            url = href.replace('amp;', '')
        else:
            url = href
        img_tag = tag.find('img')
        if not img_tag:
            return None, None
        img = img_tag.get('src')
        if not img:
            return None, None
        return url, img

    def __parse_info_style2(self, tag):
        div_tag = tag.find('div', {'class': 'yt_thumb'})
        if not div_tag:
            return None, None
        onclick = div_tag.get('onclick')
        if not onclick:
            return None, None
        style = div_tag.get('style')
        if not style:
            return None, None
        url_id = onclick.split("(")[-1].split(")")[0].split(',')[1].strip('\'')
        url = BUILD_GOOGLE_URL(url_id)
        img = style.split("(")[-1].split(")")[0]
        return url, img

    def __parse_info_style3(self, tag):
        a_tag = tag.find('a', {"target":"_blank"})
        if not a_tag:
            return None, None
        url = a_tag.get('href')
        if not url:
            return None, None
        img_tag = tag.find('img', {"alt": " (Google Drive Video) "})
        if not img_tag:
            return None, None
        img_xpath = img_tag.get('src')
        if not img_xpath:
            return None, None
        img = BUILD_URL(img_xpath)
        return url, img


    def __parse(self):
        tab_data = []

        bg_tag = self.soup.find('img', {'class': 'cover'})
        background = bg_tag.get('src')

        tab_of_top = self.__parse_tab(self.soup)
        for id, name in tab_of_top:
            tmp_tag = self.soup.find('div', {'id': id})
            tab_of_nest = self.__parse_tab(tmp_tag, prefix=name)
            if not tab_of_nest:
                tab_data.append((id, name))
            else:
                tab_data.extend(tab_of_nest)

        for id, name in tab_data:
            div_tag = self.soup.find('div', {'id': id})

            raw_data1 = div_tag.find('span')
            raw_data2 = div_tag.find('div', {'class': 'yt_thumb'})
            raw_data3 = div_tag.find('a')
            if raw_data1:
                # print('1 match - <span>')
                url, thumb = self.__parse_info_style1(div_tag)
                if not url or not thumb:
                    continue
            elif raw_data2:
                # print('2 match - <div class="yt_thumb">')
                url, thumb = self.__parse_info_style2(div_tag)
                if not url or not thumb:
                    continue
            elif raw_data3:
                # print('3 match - <a>')
                url, thumb = self.__parse_info_style3(div_tag)
                if not url or not thumb:
                    continue
            else:
                continue
            self.episodes_list.append(Episode(name, url, thumb, background))

    def get_list(self):
        return self.episodes_list


class Anime:
    def __init__(self, name = None, url = None, thumb = None):
        self.name = self._to_str_type(name)
        self.url = self._to_str_type(url)
        self.thumb = self._to_str_type(thumb)

    def _to_str_type(self, value):
        if not value:
            return
        if isinstance(value, str):
            return value
        return value.encode('utf8')

    @property
    def name(self):
        return self.__name

    @name.setter
    def name(self, value):
        self.__name = value

    @property
    def thumb(self):
        return self.__thumb

    @thumb.setter
    def thumb(self, value):
        self.__thumb = value

    @property
    def url(self):
        return self.__url

    @url.setter
    def url(self, value):
        self.__url = value


class ParserAnimeFrom2dGate:
    def __init__(self):
        self.target_url = 'http://2d-gate.org/forum-78-1.html'
        self.first_page = self.target_url
        self.class_data ={}

    @property
    def next_page(self):
        return self.__next_page

    @next_page.setter
    def next_page(self, value):
        self.__next_page = value

    @property
    def last_page(self):
        return self.__last_page

    @last_page.setter
    def last_page(self, value):
        self.__last_page = value

    def __process_animes(self, url):
        req = requests.get(url)
        soup = BeautifulSoup(req.text, 'html.parser')

        # Find next page
        nex_tag = soup.find('a', 'nxt')
        if nex_tag:
            self.next_page = nex_tag.get('href').encode('utf8')
        else:
            self.next_page = None

        # Find last page
        last_tag = soup.find('a', 'last')
        if last_tag:
            self.last_page = last_tag.get('href').encode('utf8')
        else:
            self.last_page = None

        animes = []
        for tag in soup.find_all('a', 'z'):
            name = tag.get('title')
            url = tag.get('href')

            img_tag = tag.find('img')
            if not img_tag:
                continue
            img_str = img_tag.get('src')
            img = img_str.split('src=')[-1]
            animes.append(Anime(name=name, url=url, thumb=img))
        return animes

    def get_page(self, url):
        return self.__process_animes(url)

    def __process_html(self, url):
        self.req = requests.get(url)
        self.soup = BeautifulSoup(self.req.text, 'html.parser')
        self.classes = self.soup.find('table', id='olAL')

    def __get_thumb(self, url):
        req = requests.get(url)
        soup = BeautifulSoup(req.text, 'html.parser')
        thumb = soup.find('meta', property='og:image').get('content')
        if not thumb:
            return ''
        else:
            return thumb

    def __process_content(self):
        for item in self.classes:
            class_name = item.find('th').text.encode('utf8')
            if not self.class_data.has_key(class_name):
                self.class_data.setdefault(class_name, [])
            contenet = self.class_data.get(class_name)

            for unit in item.find_all('a'):
                name = unit.find('div').next_element
                url = BUILD_URL(unit.get('href'))
                contenet.append(Anime(name, url))

    def get_classes(self):
        self.__process_html(self.target_url)

        if not self.class_data.has_key('classes'):
            self.class_data.setdefault('classes', [])
        classes = self.class_data.get('classes')
        for item in self.classes:
            classes.append(item.find('th').text.encode('utf8'))
        return classes

    def get_content(self, value):
        self.get_classes()

        name_list = []
        if not self.class_data.has_key(value):
            self.__process_content()

        content = self.class_data.get(value)
        for anime in content:
            name_list.append(anime.name)
        return name_list

    def get_thumb(self, class_name, anime_name):
        if not self.class_data.has_key(class_name):
            return ''

        content = self.class_data.get(class_name)
        for anime in content:
            if anime_name != anime.name:
                continue
            if not anime.thumb:
                anime.thumb = self.__get_thumb(anime.url)
            return anime.thumb
        return ''

    def get_url(self, class_name, anime_name):
        if not self.class_data.has_key(class_name):
            return ''

        content = self.class_data.get(class_name)
        for anime in content:
            if anime_name != anime.name:
                continue
            return '' if not anime.url else anime.url

    def get_target_url(self):
        return self.target_url


def search_in_2D_gate(q_str):
    result = []
    url = 'https://www.google.com.tw/search'
    headers = {'User-Agent': 'Mozilla/5.0 Gecko/20100101 Firefox/46.0'}
    req = requests.get(url, params={'q':'%s+site:http://2d-gate.org' % q_str}, headers = headers)

    pat = re.compile("^http://2d.gate.org")
    soup = BeautifulSoup(req.text, 'html.parser')
    for tag in soup.find_all('a'):
        link = tag.get('href')
        if not link:
            continue
        if not pat.match(link):
            continue
        if not tag.string:
            continue
        result.append((tag.string.encode('utf8'), link))
    return result


if __name__ == '__main__':
    obj = ParserAnimeFrom2dGate()

