# wechat-me
Training a wechat version of you. 用微信聊天数据训练微信版的你 aka wechat-me. 

模型可选Qwen1.5, Yi, InterLM2, ChatGLM3, Baichuan2等。

## 安装

0. 收集微信聊天数据

- macos可参考: 
  - https://github.com/BlueMatthew/WechatExporter **注：后续教程数据处理只适配此方案**
  - https://github.com/tsycnh/WeChatExporter

- windows可参考:
  - https://github.com/LC044/WeChatMsg
  - https://github.com/xaoyaoo/PyWxDump

0.1 参考[WechatExporter](https://github.com/BlueMatthew/WechatExporter)导出个人聊天数据。建议只使用双人对话数据。导出后数据格式示例(其中chat为朋友的id)：
```shell
./
├── chat.html
├── chat_files
│   └── Data
│       ├── msg-1.js
│       ├── msg-10.js
│       ├── msg-11.js
│       ├── msg-12.js
│       ├── msg-13.js
│       ├── msg-14.js
│       ├── msg-15.js
│       ├── msg-2.js
│       ├── msg-3.js
│       ├── msg-4.js
│       ├── msg-5.js
│       ├── msg-6.js
│       ├── msg-7.js
│       ├── msg-8.js
│       └── msg-9.js
```     

1. 配置wechat-tools
```bash
git clone https://github.com/metame-ai/wechat-me.git
cd wechat-me
pip install -r requirements.txt
```


2. 安装lit-gpt-chinese

- 参考流程安装环境：[lit-gpt-chinese](https://github.com/metame-ai/lit-gpt-chinese?tab=readme-ov-file#setup)

- 参考教程下载模型并进行验证：[下载Yi模型](https://github.com/metame-ai/lit-gpt-chinese/blob/chinese/tutorials/download_yi.md)
  - 模仿上述流程，可下载Qwen1.5, Yi, InterLM2, ChatGLM3, Baichuan2等模型。


## 数据处理及训练

1. 按照belle数据格式处理抓取的微信数据

```bash
cd wechat-me
python wechat/parse_chat.py --chat_file path-to-chat.html --gpt="right" --num_round=20 --over
laps=15
# gpt: "right" or "left"，指定对话数据在html中的位置，right表示让gpt扮演右边的角色，left表示让gpt扮演左边的角色 
# num_round: 每条数据中对话的轮数
# over_laps: 前后两条数据中对话重叠轮数
```

生成json文件如：out_chat_right_20-15.json

2. 训练LoRA (以Qwen1.5为例)

```bash
cd lit-gpt-chinese
mkdir -p data/metame_qwen/
cp path-to-wechat-me/out_chat_right_20-15.json data/metame_qwen/
```
- 根据需求修改: `scripts/prepare_metame_qwen.py` 中的`CHECKPOINT_DIR, SYSTEM_MESSAGE`

- 运行: `python scripts/prepare_metame_qwen.py`

- 根据需求修改: `metame/finetune_lora_qwen.sh` 中的 `io.checkpoint_dir, io.out_dir`等参数

- 运行: `bash metame/finetune_lora_qwen.sh` 开始训练

3. 效果测试

```bash
CUDA_VISIBLE_DEVICES=0 python chat/lora.py --lora_path ./out/lora/metame_qwen15_7b/iter-000960-ckpt.pth --checkpoint_dir ./checkpoints/qwen/Qwen1.5-7B-Chat  --precision "bf16-true" --system_message "#whatever-it-is"
```