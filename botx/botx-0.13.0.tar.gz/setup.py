# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['botx', 'botx.dependencies', 'botx.middlewares', 'botx.models']

package_data = \
{'': ['*']}

install_requires = \
['httpx>=0.11.0,<0.12.0', 'loguru>=0.4.0,<0.5.0', 'pydantic>=1.0,<2.0']

extras_require = \
{'docs': ['mkdocs>=1.0,<2.0',
          'mkdocs-material>=4.4,<5.0',
          'mkdocstrings>=0.7,<0.8',
          'markdown-include>=0.5.1,<0.6.0',
          'fastapi>=0.47.0,<0.48.0'],
 'tests': ['starlette>=0.12.9,<0.13.0']}

setup_kwargs = {
    'name': 'botx',
    'version': '0.13.0',
    'description': 'A little python framework for building bots for eXpress',
    'long_description': '<h1 align="center">pybotx</h1>\n<p align="center">\n    <em>A little python framework for building bots for eXpress messenger.</em>\n</p>\n<p align="center">\n    <a href="https://travis-ci.org/ExpressApp/pybotx">\n        <img src="https://travis-ci.org/ExpressApp/pybotx.svg?branch=master" alt="Travis-CI">\n    </a>\n    <a href="https://github.com/ambv/black">\n        <img src="https://img.shields.io/badge/code%20style-black-000000.svg" alt="Code Style">\n    </a>\n    <a href="https://pypi.org/project/botx/">\n        <img src="https://badge.fury.io/py/botx.svg" alt="Package version">\n    </a>\n    <a href="https://github.com/ExpressApp/pybotx/blob/master/LICENSE">\n        <img src="https://img.shields.io/github/license/Naereen/StrapDown.js.svg" alt="License">\n    </a>\n</p>\n\n\n---\n\n# Introduction\n\n`pybotx` is a framework for building bots for eXpress providing a mechanism for simple \nintegration with your favourite web frameworks.\n\nMain features:\n\n * Simple integration with your web apps.\n * Asynchronous API with synchronous as a fallback option.\n * 100% test coverage.\n * 100% type annotated codebase.\n \n \n**NOTE**: *This library is under active development and its API may be unstable. Please lock the version you are using at the minor update level. For example, like this in `poetry`.*\n\n```toml\n[tool.poetry.dependencies]\nbotx = "^0.13.0"\n```\n\n---\n\n## Requirements\n\nPython 3.6+\n\n`pybotx` use the following libraries:\n\n* <a href="https://github.com/samuelcolvin/pydantic" target="_blank">pydantic</a> for the data parts.\n* <a href="https://github.com/encode/httpx" target="_blank">httpx</a> for making HTTP calls to BotX API.\n* <a href="https://github.com/Delgan/loguru" target="_blank">loguru</a> for beautiful and powerful logs.\n* **Optional**. <a href="https://github.com/encode/starlette" target="_blank">Starlette</a> for tests.\n\n## Installation\n```bash\n$ pip install botx\n```\n\nOr if you are going to write tests:\n\n```bash\n$ pip install botx[tests]\n```\n\nYou will also need a web framework to create bots as the current BotX API only works with webhooks. \nThis documentation will use <a href="https://github.com/tiangolo/fastapi" target="_blank">FastAPI</a> for the examples bellow.\n```bash\n$ pip install fastapi uvicorn\n```\n\n## Example\n\nLet\'s create a simple echo bot.\n\n* Create a file `main.py` with following content:\n```python3\nfrom botx import Bot, ExpressServer, IncomingMessage, Message, Status\nfrom fastapi import FastAPI\nfrom starlette.status import HTTP_202_ACCEPTED\n\nbot = Bot(known_hosts=[ExpressServer(host="cts.example.com", secret_key="secret")])\n\n\n@bot.default(include_in_status=False)\nasync def echo_handler(message: Message) -> None:\n    await bot.answer_message(message.body, message)\n\n\napp = FastAPI()\napp.add_event_handler("shutdown", bot.shutdown)\n\n\n@app.get("/status", response_model=Status)\nasync def bot_status() -> Status:\n    return await bot.status()\n\n\n@app.post("/command", status_code=HTTP_202_ACCEPTED)\nasync def bot_command(message: IncomingMessage) -> None:\n    await bot.execute_command(message.dict())\n```\n\n* Deploy a bot on your server using uvicorn and set the url for the webhook in Express.\n```bash\n$ uvicorn main:app --host=0.0.0.0\n```\n\nThis bot will send back every your message.\n\n## License\n\nThis project is licensed under the terms of the MIT license.\n',
    'author': 'Sidnev Nikolay',
    'author_email': 'nsidnev@ccsteam.ru',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/ExpressApp/pybotx',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
