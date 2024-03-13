#!/usr/bin/env python3
import re
import glob
import os
from bs4 import BeautifulSoup
import json


def parse_html(html_str):
    if os.path.isfile(html_str):
        html_str = open(html_str, 'r').read()

    soup = BeautifulSoup(html_str, 'html.parser')

    messages = []

    num_failed = 0
    for msg_div in soup.find_all('div', class_='msg'):
        if ' '.join(msg_div['class']) in ['msg chat-notice']:
            print('skip notice with msgid: ', msg_div['msgid'])
            continue
        if 'msgtype' not in msg_div.attrs:
            print(msg_div)
            num_failed += 1
            continue
        msgtype = msg_div['msgtype']
        if '_' in msg_div['msgid']:
            # group chat
            continue
        msgid = int(msg_div['msgid'])
        sender = 'left' if 'left' in msg_div['class'] else 'right'

        avatar = msg_div.find('img')['src']
        dspname = msg_div.find('span', class_='dspname').text
        timestamp = msg_div.find('div', class_='nt-box').text.split()[-1]

        if msgtype in ['1']:  # Text message
            message = msg_div.find('span', class_='msg-text').text.strip()
            if message.startswith('http'):
                continue
            # message = message.encode('utf-16','surrogatepass').decode('utf-16')
        elif msgtype == "image":  # Image message
            continue
            rawurl = msg_div.find('img', class_='image')['rawurl']
            message = {
                "rawurl": rawurl,
                "thumbnail": msg_div.find('img', class_='image')['src']
            }
        elif msgtype == "47":  #
            # print(f"skip msgtype: {msgtype}, msgid: {msgid}, possibly emoji")
            continue
        elif msgtype == "49":  #
            message = ''
            msg_text_all = msg_div.find_all('span', class_='msg-text')
            for msg_text in msg_text_all:
                message += msg_text.text.strip() + '\n'
        else:
            print(f'unknown msgtype: {msgtype} -- msgid: {msg_div["msgid"]}')
            continue

        if not len(message):
            # print(f'----- empty message ----- msgid: {msg_div["msgid"]}')
            continue

        message_data = {
            "msgtype": msgtype,
            "msgid": msgid,
            "content": {
                "avatar": avatar,
                "dspname": dspname,
                "timestamp": timestamp,
                "message": message
            },
            "sender": sender
        }

        messages.append(message_data)

    print(f"total messages: {len(messages)}, failed: {num_failed}")
    return messages


def write_json(messages, output_file):
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(json.dumps(messages, indent=2, ensure_ascii=False).encode(
            'utf-16','surrogatepass').decode('utf-16'))
    print(f"write to {output_file}")


def parse_html_file(html_file):
    output = parse_html(html_file)
    basename = os.path.basename(html_file).split('.')[0]
    res_file = f'{basename}_output.json'
    res_list = filter_quote(output)
    res_list = to_belle_formate(res_list)
    write_json(res_list, res_file)


def parse_js_file(js_file):
    # 读取 JavaScript 文件
    with open(js_file, 'r', encoding='utf-8') as f:
        js_content = f.read()

    basename = os.path.basename(js_file).split('.')[0]
    # 使用正则表达式提取变量数组内容
    match = re.search(r'var msgArray = (\[.*?\]);', js_content, re.DOTALL)
    if match:
        array_str = match.group(1)
        # 将字符串表示的数组转换为 Python 列表
        my_array = eval(array_str)
        output = parse_html(''.join(my_array))
        # write_json(output, f'{basename}_output.json')
        return output
    else:
        print("Variable array not found in the JavaScript file.")


def parse_chat(chat_file, gpt='right', num_round=20, overlaps=15):
    data_dir = os.path.dirname(chat_file)
    basename = os.path.basename(chat_file).split('.')[0]
    js_file_list = sorted(glob.glob(f"{data_dir}/{basename}_files/Data/*.js"))

    output = parse_html(chat_file)
    for js_file in js_file_list:
        print(f'--- parsing', js_file)
        output += parse_js_file(js_file)

    output = sorted(output, key=lambda x: x['msgid'])
    print(f"total messages: {len(output)}")
    output_file = f'out_{basename}_{gpt}_{num_round}-{overlaps}.json'
    write_json(output, output_file.replace('out_', 'out_raw_'))
    output = filter_quote(output)
    output = to_belle_formate(output, gpt=gpt, num_round=num_round, overlaps=overlaps)
    print(f"total conversations: {len(output)}")

    write_json(output, output_file)
    print(f"save to {output_file}")


def filter_quote(messages):
    res_list = []
    last_sender = None
    for msg in messages:
        if msg['msgtype'] in ['image']:
            continue
        msg['content']['message'] = msg['content']['message'].split('\n')[-1]
        if not len(msg['content']['message']):
            continue
        msg['content']['message'] += '\n'
        sender = msg['sender']
        if len(res_list) and sender == last_sender:
            if not msg['content']['message'].startswith('- - -'):
                res_list[-1]['content']['message'] += msg['content']['message']
        else:
            res_list.append(msg)
        last_sender = sender
    return res_list


def to_belle_formate(messages, gpt='right', num_round=20, overlaps=15):
    res = []
    idx = 0
    while messages[idx]['sender'] == gpt:
        idx += 1

    while idx < len(messages):
        res.append(messages[idx:idx+num_round*2])
        idx += (num_round - overlaps) * 2
    '''
    {
    "id": "27684",
    "conversations": [
    {
        "from": "human",
        "value": "你好，请问你能帮我查一下明天的天气吗？\n"
    },
    {
        "from": "gpt",
        "value": "当然，你在哪个城市呢？\n"
    },
    ]
    },
    '''
    res_list = []
    for i, conv in enumerate(res):
        conv_list = []
        for msg in conv:
            _from = 'gpt' if msg['sender'] == gpt else 'human'
            # 中间换行符号变为句号
            text = msg['content']['message'].strip()
            text = "。".join(text.split("\n")) + "\n"
            conv_list.append({
                "from": _from,
                "value": text
            })
        res_list.append({
            "id": str(i),
            "conversations": conv_list
        })
    return res_list


if __name__ == '__main__':
    import fire
    fire.Fire(parse_chat)

# vim: ts=4 sw=4 sts=4 expandtab
