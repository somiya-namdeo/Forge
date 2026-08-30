with open('README.md', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace('src="frontend/', 'src="./frontend/')
content = content.replace('src="docs/', 'src="./docs/')

with open('README.md', 'w', encoding='utf-8') as f:
    f.write(content)