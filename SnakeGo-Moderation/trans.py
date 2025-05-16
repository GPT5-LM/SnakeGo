import json
import os

# 定义输入和输出文件名
input_filename = "dataset.json"
output_filename = "fine_tuning.jsonl"

# 检查输入文件是否存在
if not os.path.exists(input_filename):
    print(f"错误：输入文件 '{input_filename}' 未找到。请确保文件存在并位于脚本同一目录。")
    exit()

# 从输入文件读取数据
try:
    with open(input_filename, 'r', encoding='utf-8') as f:
        input_data = json.load(f)
    print(f"成功从 '{input_filename}' 加载数据。")
except json.JSONDecodeError:
    print(f"错误：无法解析文件 '{input_filename}' 中的 JSON。请检查文件格式是否正确。")
    exit()
except Exception as e:
    print(f"读取文件 '{input_filename}' 时发生意外错误：{e}")
    exit()

# 检查加载的数据是否为列表，因为我们期望输入是一个 JSON 数组
if not isinstance(input_data, list):
    print(f"错误：文件 '{input_filename}' 的内容应为一个 JSON 数组（列表），但加载到的是 {type(input_data).__name__}。请确保文件包含一个对象列表。")
    exit()

# 将数据转换为 JSONL 格式并写入输出文件
try:
    with open(output_filename, 'w', encoding='utf-8') as f:
        # 遍历输入数据列表
        for i, item in enumerate(input_data):
            # 确保列表中的每个元素都是字典
            if isinstance(item, dict):
                # 从当前字典中提取 'text' 字段的值
                # 使用 .get() 方法更安全，如果键不存在则返回空字符串
                text_content = item.get("text", "")

                # 构建符合 JSONL 格式的新字典
                output_dict = {"text": text_content}

                # 将新字典序列化为 JSON 字符串
                # ensure_ascii=False 确保中文字符不被转义成 \uXXXX
                # separators=(',', ':') 可以稍微减小输出文件大小，但对于可读性影响不大，这里保持默认即可
                json_line = json.dumps(output_dict, ensure_ascii=False)

                # 将 JSON 字符串写入文件，并在末尾添加换行符
                f.write(json_line + '\n')
            else:
                print(f"警告：跳过输入数据中索引为 {i} 的非字典项。期望一个字典，但得到的是 {type(item).__name__}: {item}")


    print(f"数据已成功转换为 JSONL 格式并保存到文件: {output_filename}")

except IOError as e:
    print(f"写入输出文件 '{output_filename}' 时发生错误：{e}")
except Exception as e:
    print(f"处理数据时发生意外错误：{e}")

