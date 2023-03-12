import nox

LIBNAME = "translate_md"
SOURCE = "src/translate_md"

def install_dev_requirements(session, filename="all.txt"):
    session.run("pip", "install", "-r", f"requirements/{filename}")

def install(session, cli=False):
    if not cli:
        session.run("pip", "install", ".")
    else:
        session.run("pip", "install", ".[cli]")


@nox.session
def coverage(session):
    install_dev_requirements(session, filename="test.txt")
    install(session)
    session.run(
        "python",
        "-m",
        "pytest",
        "tests",
        f"--cov={LIBNAME}",
        "--cov-report=term-missing",
        "--cov-report=xml",
        "--cov-config=pyproject.toml",
    )

@nox.session
def lint(session):
    session.install("black", "ruff")
    session.run("ruff", SOURCE)
    session.run("black", "--check", SOURCE)


@nox.session
def typecheck(session):
    install_dev_requirements(session, filename="all.txt")
    install(session, cli=True)
    session.run("mypy", "-p", "src", "--no-incremental")


@nox.session(reuse_venv=True)
def format(session):
    session.install("black", "ruff")
    session.run("ruff", SOURCE, "--fix")
    session.run("black", SOURCE)


@nox.session
def build(session):
    session.install("hatch")
    session.run("hatch", "build")


@nox.session
def publish(session):
    session.notify("build")
    session.run("hatch", "publish")
