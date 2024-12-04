import datetime


def format_prompt(prompt: str, **kwargs):
    kwargs.update({"current_datetime": datetime.datetime.now().isoformat()})
    return prompt.format(**kwargs)


QUERY_INTERPRETER_SYSTEM_PROMPT = """
用户正在搜索一些文档。输入文本是用户用自然语言编写的规范。
生成一个相应的 SQL select 语句对应给定的规范，并将其包装在一个 SQL 代码块中。

模式：
- `documents`：包含所有文档的表。
    - `content_type`: STRING - 文档内容的类型。可以是 'text'（文本文档）或 'image'（图片文档）。
    - `title`: STRING - 文档的标题。
    - `description`: STRING - 文档内容的语义描述。
    - `text`: STRING - 文档包含的文本。
    - `created_at`: DATE - 文档创建日期。

注意：
- 支持 SLIKE（Semantic LIKE）和 NSLIKE（Not SLIKE）操作符，可用于 STRING 类型的语义相关性匹配。
- 如果用户没有明确指定要查询哪一方面，默认情况下用户是按 `description` 的语义来查询的。
- 只有用户明确指定按文本查询的时候，再用 LIKE、NOT LIKE、= 或 <> 来匹配 `text` 字段。
- 您的查询应严格遵循模式。
- SELECT 和 FROM 子句不应更改。
- 对于日期比较，您只能使用 <、>、<=、>=、=、<>、BETWEEN 操作符，且绝不能使用任何SQL函数。
- 除了 SLIKE 和 NSLIKE 外，不要使用任何 SQL 方言特定的用法。
- 不要使用任何子查询或表连接。
- AND 的优先级高于 OR，所以在必要的地方加括号。


最新信息：
- 当前日期和时间：{current_datetime}

您的输出格式（当用户查询有效时）：
```sql
SELECT * FROM documents
WHERE <条件表达式>
;
```
"""

IMAGE_PREPROCESSOR_SYSTEM_PROMPT = """
使用 JSON 文档描述给定的图像，并将其包装在一个代码块中。

注意：
- 您的输出应精确地表示图像的语义细节。

您的输出格式：
```json
{{
    "文本": <字符串列表（提取图像中的所有文本内容；如果没有文本，则为空列表）>,
    "描述": <字符串（总结图像内容）>
}}
```
"""

TEXT_PREPROCESSOR_SYSTEM_PROMPT = """
使用 JSON 文档描述给定的文本文件，并将其包装在一个代码块中。

注意：
- 您的输出应精确地表示文本的语义细节。
- 您的输出不应包含任何未提及的信息。

您的输出格式：
```json
{{
    "描述": <字符串（总结文件内容）>
}}
```
"""
