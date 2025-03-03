# 获取快手直播的真实流媒体地址，默认输出最高画质
# https://live.kuaishou.com/u/KPL704668133
# 如获取失败，尝试修改 cookie 中的 did

import requests


class KuaiShou:
    def __init__(self, rid):
        self.rid = rid

    def get_real_urls(self):
        headers = {
            'Host': 'live.kuaishou.com',
            'Connection': 'keep-alive',
            'Cache-Control': 'max-age=0',
            'sec-ch-ua': '"Not(A:Brand";v="99", "Google Chrome";v="133", "Chromium";v="133"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'DNT': '1',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-User': '?1',
            'Sec-Fetch-Dest': 'document',
            'Accept-Encoding': 'gzip, deflate, br, zstd',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,zh-TW;q=0.7,en-US;q=0.6',
            'Cookie': 'did=web_e639ba9de018062cc0a1b178c9f56543'
        }
        url = f'https://live.kuaishou.com/u/{self.rid}'
        with requests.Session() as s:
            res = s.get(url, headers=headers, verify=False, proxies={"http": None, "https": None})
            print(f"状态码: {res.status_code}")
            text = res.text
            # 查找 playList 数据
            start_idx = text.find('"playList":')
            if start_idx == -1:
                raise Exception('未找到 playList 数据')
            # 找到 playList 数组的结束位置
            bracket_count = 0
            end_idx = start_idx
            for i, char in enumerate(text[start_idx:], start=start_idx):
                if char == '[':
                    bracket_count += 1
                elif char == ']':
                    bracket_count -= 1
                    if bracket_count == 0:
                        end_idx = i + 1
                        break
            if end_idx == start_idx:
                raise Exception('无法解析 playList 数据')

            # 提取 playList 字符串
            playlist_str = text[start_idx:end_idx]
            if not playlist_str:
                raise Exception('直播间不存在或未开播')

            # 手动提取 representation 块
            result = []
            for codec in ['"h264":', '"hevc":']:
                codec_start = playlist_str.find(codec)
                if codec_start == -1:
                    continue
                rep_start = playlist_str.find('"representation":', codec_start)
                if rep_start == -1:
                    continue
                # 找到 representation 数组的开始和结束
                array_start = playlist_str.find('[', rep_start)
                array_end = array_start
                rep_str = playlist_str[array_start:]
                while True:
                    block_start = rep_str.find('{')
                    if block_start == -1:
                        break
                    bracket_count = 1
                    block_end = block_start
                    for i, char in enumerate(rep_str[block_start + 1:], start=block_start + 1):
                        if char == '{':
                            bracket_count += 1
                        elif char == '}':
                            bracket_count -= 1
                            if bracket_count == 0:
                                block_end = i + 1
                                break
                    if block_end == block_start:
                        break
                    # 提取单个 representation 块
                    block = rep_str[block_start:block_end]
                    url_start = block.find('"url":"') + 7
                    if url_start == 6:  # 未找到 "url"
                        break
                    url_end = block.find('",', url_start)
                    url = block[url_start:url_end].replace('\\u002F', '/')

                    name_start = block.find('"name":"') + 8
                    if name_start == 7:  # 未找到 "name"
                        break
                    name_end = block.find('",', name_start)
                    name = block[name_start:name_end]

                    result.append({'url': url, 'name': name})
                    # 移动到下一个块
                    rep_str = rep_str[block_end:]
            if result:
                return result
            raise Exception('未找到有效的播放地址')


def get_real_urls(rid):
    try:
        ks = KuaiShou(rid)
        return ks.get_real_urls()
    except Exception as e:
        print('Exception：', e)
        return False


if __name__ == '__main__':
    r = input('请输入快手直播房间ID：\n')
    urls = get_real_urls(r)
    if urls:
        for item in urls:
            print(f"清晰度: {item['name']}, 直链: {item['url']}")
    else:
        print("获取失败")