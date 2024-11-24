import datetime


def format_prompt(prompt: str, **kwargs):
    kwargs.update({"current_datetime": datetime.datetime.now().isoformat()})
    return prompt.format(**kwargs)


QUERY_INTERPRETER_SYSTEM_PROMPT = """
The user queries for some entities from a storage base.
Generate a respective SQL query for the given user query in natural language, wrapped in a SQL code block.
If the user query is not valid or cannot be interpreted, return an empty SQL statement.

Notes:
- The table schema is not given, so you can decide field names on your own.
- Select and from clauses shouldn't be changed.
- Category of the entity should be considered in the condition.
- Try your best to break down keywords into smaller pieces to make the query more fine-grained.
- Always prefer attribute comparison rather than text matching whenever possible.
- Always prefer date comparison over numerical comparison whenever possible.
- Avoid ambiguous or unclear field names.
- Avoid ID-like field names.
- Don't use any dialect-specific syntaxes.
- Don't use any subqueries or table joins.
- `AND` has a higher precedence than `OR`.

Latest information:
- Current time: {current_datetime}

Your output format (when user query is valid):
```sql
SELECT * FROM db
WHERE <condition expression>
;
```
Your output format (when user query is not valid):
```sql
;
```
"""

IMAGE_PREPROCESSOR_SYSTEM_PROMPT_YAML = """
Describe the given image using a YAML document, wrapped in a code block.

Notes:
- Your output should conform to the YAML syntax.
- Your output should precisely represent the image details.
- Your output should include some supplementary attributes at the end.

Your output format:
```yaml
image:
    content: <nested dictionary (describe the image in a structured and detailed manner)>
    text: <list of strings (extract the text in its original language, if there is any text>
    description: <string (summarize the core content)>
    title: <string (a reasonable name for the image)>
    tags: <list of strings>
    context: <string>
    <some attribute>: <value>
    <some attribute>: <value>
    <...>
```
"""


IMAGE_PREPROCESSOR_SYSTEM_PROMPT = """
Describe the given image using a JSON document, wrapped in a code block.

Notes:
- Your output should conform to the JSON syntax.
- Your output should precisely represent the image details.
- Your output should include some supplementary attributes at the end.

Your output format:
```json
{{
    "image": {{
        "content": <nested dictionary (describe the image in a structured and detailed manner)>,
        "text": <list of strings (extract the text in its original language, if there is any text)>,
        "description": <string (summarize the core content)>,
        "title": <string (a reasonable name for the image)>,
        "tags": <list of strings>,
        "context": <string>,
        "<some attribute>": <value>,
        "<some attribute>": <value>,
        <...>
    }}
}}
```
"""

TEXT_PREPROCESSOR_SYSTEM_PROMPT = """
Describe the given text using a YAML list, wrapped in a code block.

Notes:
- Your output should conform to the YAML syntax.
- Your output should precisely represent the semantic details of the text.
- Your output should include some supplementary attributes at the end.
- Your output should never contain any unmentioned information.

Your output format:
```yaml
text:
    text_sections: <list of strings (divide the ORIGINAL text into small, semantically coherent sections, WITHOUT simplifying or summarizing)>
    summary: <string (summarize the core content)>
    title: <string (a reasonable title for the text)>
    tags: <list of strings>
    context: <string>
    <some attribute>: <value>
    <some attribute>: <value>
    <...>
```
"""
