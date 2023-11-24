# This file is dual licensed under the terms of the Apache License, Version
# 2.0, and the BSD License. See the LICENSE file in the root of this repository
# for complete details.


import getpass
import io
import json
import os
import subprocess
import time
import zipfile

import click
import requests


def run(*args, **kwargs):
    print(f"[running] {list(args)}")
    subprocess.check_call(list(args), **kwargs)


def wait_for_build_complete_github_actions(session, token, run_url):
    while True:
        response = session.get(
            run_url,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"token {token}",
            },
        )
        response.raise_for_status()
        if response.json()["conclusion"] is not None:
            break
        time.sleep(3)


def download_artifacts_github_actions(session, token, run_url):
    response = session.get(
        run_url,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"token {token}",
        },
    )
    response.raise_for_status()

    response = session.get(
        response.json()["artifacts_url"],
        headers={
            "Content-Type": "application/json",
            "Authorization": f"token {token}",
        },
    )
    response.raise_for_status()
    paths = []
    for artifact in response.json()["artifacts"]:
        response = session.get(
            artifact["archive_download_url"],
            headers={
                "Content-Type": "application/json",
                "Authorization": f"token {token}",
            },
        )
        with zipfile.ZipFile(io.BytesIO(response.content)) as z:
            for name in z.namelist():
                if not name.endswith((".whl", ".tar.gz")):
                    continue
                p = z.open(name)
                out_path = os.path.join(
                    os.path.dirname(__file__),
                    "dist",
                    os.path.basename(name),
                )
                with open(out_path, "wb") as f:
                    f.write(p.read())
                paths.append(out_path)
    return paths


def build_github_actions_sdist_wheels(token, version):
    session = requests.Session()

    response = session.post(
        "https://api.github.com/repos/pyca/bcrypt/actions/workflows/"
        "wheel-builder.yml/dispatches",
        headers={
            "Content-Type": "application/json",
            "Accept": "application/vnd.github.v3+json",
            "Authorization": f"token {token}",
        },
        data=json.dumps({"ref": "main", "inputs": {"version": version}}),
    )
    response.raise_for_status()

    # Give it a few seconds for the run to kick off.
    time.sleep(5)
    response = session.get(
        (
            "https://api.github.com/repos/pyca/bcrypt/actions/workflows/"
            "wheel-builder.yml/runs?event=workflow_dispatch"
        ),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"token {token}",
        },
    )
    response.raise_for_status()
    run_url = response.json()["workflow_runs"][0]["url"]
    wait_for_build_complete_github_actions(session, token, run_url)
    return download_artifacts_github_actions(session, token, run_url)


@click.command()
@click.argument("version")
def release(version):
    """
    ``version`` should be a string like '0.4' or '1.0'.
    """
    github_token = getpass.getpass("Github person access token: ")

    run("git", "tag", "-s", version, "-m", f"{version} release")
    run("git", "push", "--tags")

    github_actions_paths = build_github_actions_sdist_wheels(
        github_token, version
    )

    run("twine", "upload", *github_actions_paths)


if __name__ == "__main__":
    release()
