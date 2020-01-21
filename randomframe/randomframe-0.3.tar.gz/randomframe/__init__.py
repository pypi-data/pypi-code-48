import json
import logging
import random
from typing import List, Optional, Callable

import base58
import requests
from flask import Blueprint, render_template, jsonify, request, Response, abort

logger = logging.getLogger("randomframe")


class RandomFrame:
    def __init__(self, key: str, name: str, filefunc: Callable[[str], str] = None):
        self.key = key
        self.name = name
        self.filefunc = filefunc or (lambda f: f)

    @property
    def api_host(self):
        return "frames.ms.jboi.dev"  # todo move to env

    def get_list(self) -> List[str]:
        return requests.get(f"https://{self.api_host}/list/{self.key}").json()

    def get_file(self, file: str) -> int:
        return requests.get(f"https://{self.api_host}/list/{self.key}/{file}").json()

    def generate_list(self, get: Optional[list] = None):
        files = self.get_list()
        if get is not None:
            files = [f for f in files if f in get]
        return files

    def pick_random(self, l: list):
        file = random.choice(l)
        frame_num = self.get_file(file)
        return dict(file=self.filefunc(file), frame=random.choice(range(0, frame_num)))

    def get_frame(
        self, file: str, frame: int, thumb: bool = False, filename: Optional[str] = None
    ) -> Response:
        path = f"{'frame' if not thumb else 'thumb'}/{self.key}/{file}/{frame}"
        r = requests.get(f"https://{self.api_host}/{path}")

        if r.status_code != 200:
            logger.warning(f"{path!r} did not wield a 200 response: {r.status_code}")
            return abort(400)

        filename = filename or f'{file}_{"t" if thumb else ""}_{frame}'

        return Response(
            r.content,
            status=200,
            headers={
                "Content-Disposition": rf'{"attachment; " if "dl" in request.args else ""}filename="{filename}.png"',
                "Content-Type": "image/png",
            },
        )

    def generate_blueprint(self) -> Blueprint:
        blueprint = Blueprint(
            "randomframe",
            __name__,
            template_folder="templates",
            static_folder="static",
            static_url_path="/static/randomframe",
        )

        @blueprint.route("/")
        def index():
            return render_template("index.html", name=self.name)

        @blueprint.route("/list")
        def total_list():
            return jsonify(self.generate_list())

        @blueprint.route("/random")
        def get_random():
            get = request.args.get("in", None)
            if get is not None:
                get = json.loads(base58.b58decode(get))
            return self.pick_random(self.generate_list(get))

        return blueprint
