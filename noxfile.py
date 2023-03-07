import nox

LIBNAME = "translate_md"
SOURCE = "src/translate_md"

def install_dev_requirements(session):
    session.run("pip", "install", "-r", "dev-requirements.txt")

def install(session):
    session.run("pip", "install", ".")

@nox.session
def coverage(session):
    install_dev_requirements(session)
    install(session)
    session.run(
        "python",
        "-m",
        "pytest",
        "tests",
        f"--cov={LIBNAME}",
        "--cov-report=term-missing",
        "--cov-config=pyproject.toml",
    )

@nox.session
def lint(session):
    session.install("black", "ruff")
    session.run("ruff", SOURCE)
    session.run("black", "--check", SOURCE)


@nox.session
def typecheck(session):
    session.install("mypy")
    install_dev_requirements(session)
    session.run("mypy", "-p", SOURCE, "--no-incremental")


@nox.session(reuse_venv=True)
def format(session):
    session.install("black", "ruff")
    session.run("ruff", SOURCE, "--fix")
    session.run("black", SOURCE)
