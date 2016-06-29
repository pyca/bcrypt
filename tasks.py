from __future__ import absolute_import, division, print_function

import getpass
import io
import os
import time

from clint.textui.progress import Bar as ProgressBar

import invoke

import requests


JENKINS_URL = "https://jenkins.cryptography.io/job/bcrypt-wheel-builder"


def wait_for_build_completed(session):
    # Wait 20 seconds before actually checking if the build is complete, to
    # ensure that it had time to really start.
    time.sleep(20)
    while True:
        response = session.get(
            "{0}/lastBuild/api/json/".format(JENKINS_URL),
            headers={
                "Accept": "application/json",
            }
        )
        response.raise_for_status()
        if not response.json()["building"]:
            assert response.json()["result"] == "SUCCESS"
            break
        time.sleep(0.1)


def download_artifacts(session):
    response = session.get(
        "{0}/lastBuild/api/json/".format(JENKINS_URL),
        headers={
            "Accept": "application/json"
        }
    )
    response.raise_for_status()
    assert not response.json()["building"]
    assert response.json()["result"] == "SUCCESS"

    paths = []

    last_build_number = response.json()["number"]
    for run in response.json()["runs"]:
        if run["number"] != last_build_number:
            print(
                "Skipping {0} as it is not from the latest build ({1})".format(
                    run["url"], last_build_number
                )
            )
            continue

        response = session.get(
            run["url"] + "api/json/",
            headers={
                "Accept": "application/json",
            }
        )
        response.raise_for_status()
        for artifact in response.json()["artifacts"]:
            response = session.get(
                "{0}artifact/{1}".format(run["url"], artifact["relativePath"]),
                stream=True
            )
            assert response.headers["content-length"]
            print("Downloading {0}".format(artifact["fileName"]))
            bar = ProgressBar(
                expected_size=int(response.headers["content-length"]),
                filled_char="="
            )
            content = io.BytesIO()
            for data in response.iter_content(chunk_size=8192):
                content.write(data)
                bar.show(content.tell())
            assert bar.expected_size == content.tell()
            bar.done()
            out_path = os.path.join(
                os.path.dirname(__file__),
                "dist",
                artifact["fileName"],
            )
            with open(out_path, "wb") as f:
                f.write(content.getvalue())
            paths.append(out_path)
    return paths


@invoke.task
def release(version):
    """
    ``version`` should be a string like '0.4' or '1.0'.
    """
    invoke.run("git tag -s {0} -m '{0} release'".format(version))
    invoke.run("git push --tags")

    invoke.run("python setup.py sdist")

    invoke.run(
        "twine upload -s dist/bcrypt-{0}*".format(version)
    )

    session = requests.Session()

    token = getpass.getpass("Input the Jenkins token: ")
    response = session.post(
        "{0}/build?token={1}".format(JENKINS_URL, token),
        params={
            "cause": "Building wheels for {0}".format(version)
        }
    )
    response.raise_for_status()
    wait_for_build_completed(session)
    paths = download_artifacts(session)
    invoke.run("twine upload {0}".format(" ".join(paths)))
