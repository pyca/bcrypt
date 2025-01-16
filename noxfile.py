import nox

nox.options.reuse_existing_virtualenvs = True
nox.options.default_venv_backend = "uv|virtualenv"


@nox.session
def tests(session: nox.Session) -> None:
    session.install("coverage")
    session.install(".[tests]")

    session.run(
        "coverage", "run", "-m", "pytest", "--strict-markers", *session.posargs
    )
    session.run("coverage", "combine")
    session.run("coverage", "report", "-m", "--fail-under", "100")


@nox.session
def pep8(session: nox.Session) -> None:
    session.install("ruff")

    session.run("ruff", "check", ".")
    session.run("ruff", "format", "--check", ".")


@nox.session
def mypy(session: nox.Session) -> None:
    session.install("mypy")
    session.install(".[tests]")

    session.run("mypy", "tests/")


@nox.session
def packaging(session: nox.Session) -> None:
    session.install("setuptools-rust", "check-manifest", "readme_renderer")

    session.run("check-manifest")
    session.run(
        "python3", "-m", "readme_renderer", "README.rst", "-o", "/dev/null"
    )
