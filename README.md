# wechat-me
Training a wechat version of you. 用微信聊天数据训练微信版的你，aka wechat-me. 

支持主流中英文开源模型，如Qwen1.5, Yi, InterLM2, ChatGLM3, Baichuan2等。

## 安装wechat-me

0. 收集微信聊天数据
  - 参考WechatExporter: https://github.com/BlueMatthew/WechatExporter **注：后续教程数据处理只适配此方案**


其它抓取方式：
  - https://github.com/tsycnh/WeChatExporter
  - https://github.com/LC044/WeChatMsg
  - https://github.com/xaoyaoo/PyWxDump

0.1 参考[WechatExporter](https://github.com/BlueMatthew/WechatExporter)导出个人聊天数据，导出格式选择html。建议只使用双人对话数据。导出后数据格式示例：
```shell
./
├── 张三.html
├── 张三_files
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

## 安装litgpt-chinese

- 安装litgpt-chinese及相关依赖
```
git clone https://github.com/metame-ai/litgpt-chinese
cd litgpt-chinese
pip install -e '.[all]'
```

- 下载预训练模型，以Qwen1.5为例。(若显存不足，选更小的模型，如Qwen/Qwen1.5-0.5B-Chat)
```
cd litgpt-chinese
litgpt download --repo_id Qwen/Qwen1.5-7B-Chat
```
- (可选)测试预训练模型
```
litgpt chat \
  --checkpoint_dir checkpoints/Qwen/Qwen1.5-7B-Chat
```
  
## 数据处理及训练

- 按照belle数据格式处理抓取的微信数据

```bash
cd wechat-me
python wechat/parse_chat.py --chat_file path-to-chat.html --gpt="right" --num_round=20 --over
laps=15
# gpt: "right" or "left"，指定对话数据在html中的位置，right表示让gpt扮演右边的角色，left表示让gpt扮演左边的角色 
# num_round: 每条数据中对话的轮数
# over_laps: 前后两条数据中对话重叠轮数
```

生成对话数据json文件，如：out_chat_right_20-15.json

- 训练LoRA (以Qwen1.5-7B-Chat为例)

```bash
cd litgpt-chinese
mkdir -p data/metame/
cp path-to-wechat-me/out_chat_right_20-15.json data/metame/
```
- (可选) 根据需求修改: `metame/finetune_lora_qwen.sh` 中的 `data.system_message`等参数

- 运行: `bash metame/finetune_lora_qwen.sh` 开始训练

- 测试训练结果:

```bash
litgpt chat \
  --checkpoint_dir "out/lora/metame_qwen1-5_7b/step-xxx" \
  --precision "16-true" \
  --system_message "#whatever-it-is"
```

---
注: 更多litgpt-chinese使用方式可参考 [litgpt-chinese](https://github.com/metame-ai/litgpt-chinese?tab=readme-ov-file#using-litgpt)