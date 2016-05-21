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


class ProcessEpisodes():
    def __init__(self, url):
        self.url = url
        self.episodes_list = []
        self.__parse()

    def __parse_arch_1(self, tag):
        gd_thumb = tag.find('div', 'gd_thumb')
        if not gd_thumb:
            return None, None, None

        onclick = gd_thumb.get('onclick')
        target = onclick.split(',')[1]
        url = BUILD_GOOGLE_URL(target.strip('\''))

        style = gd_thumb.get('style')
        if not style:
            return None, None, None
        l_paren = style.rfind('(')
        r_paren = style.rfind(')')
        background = BUILD_URL(style[l_paren + 1:r_paren])

        img = gd_thumb.find('img')
        if not img:
            return None, None, None
        thumb = BUILD_URL(img.get('src'))
        return url, thumb, background

    def __parse_arch_2(self, tag):
        tag_a = tag.find('a')
        if not tag_a:
            return None, None, None
        url = tag_a.get('href')
        if not url:
            return None, None, None
        img = tag_a.find('img')
        if not img:
            return None, None, None
        thumb = background = BUILD_URL(img.get('src'))
        # Skip fake tab
        if url == thumb:
            return None, None, None
        return url, thumb, background

    def __parse(self):
        req = requests.get(self.url)
        soup = BeautifulSoup(req.text, 'html.parser')
        content = soup.find('div', style="display:none")
        if not content:
            url, thumb, background = self.__parse_arch_1(soup)
            if url and thumb and background:
                self.episodes_list.append(Episode(str('1'), url, thumb, background))
            return

        # Parse url of episodes
        info = OrderedDict()
        for tag in content.find_all('div'):
            if tag.string:
                continue
            id = tag.get('id')
            if not id:
                continue

            if tag.find('div', 'gd_thumb'):
                url, thumb, background = self.__parse_arch_1(tag)
                if not url and not thumb and not background:
                    continue

            elif tag.find('a'):
                url, thumb, background = self.__parse_arch_2(tag)
                if not url and not thumb and not background:
                    continue
            else:
                #TODO: another arch type
                continue
            info[id] = [url, thumb, background]

        # Parse number of episodes
        number_dict = {}
        for tag in content.find_all('a'):
            href = tag.get('href')
            if not href:
                continue
            if '#' not in href:
                continue
            tab = href.split('#')[-1]
            tab_content = tag.string.encode('utf8')
            number_dict[tab] = tab_content

        # Strip invalid tab
        for id in info:
            number = number_dict.get(id)
            if not number:
                continue
            url, thumb, background = info.get(id)
            # print number, url, background, thumb
            self.episodes_list.append(Episode(number, url, thumb, background))

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

