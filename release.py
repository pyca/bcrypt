# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import subprocess

import click


def run(*args, **kwargs):
    print(f"[running] {list(args)}")
    subprocess.check_call(list(args), **kwargs)


@click.command()
@click.argument("version")
def release(version):
    """
    ``version`` should be a string like '0.4' or '1.0'.
    """
    run("git", "tag", "-s", version, "-m", f"{version} release")
    run("git", "push", "--tags", "git@github.com:pyca/bcrypt.git")


if __name__ == "__main__":
    release()
