import nox

LIBNAME = "src/translate_md"

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
        # "-s",
        # "tests",
        f"--cov={LIBNAME}",
        "--cov-report=term-missing",
        # "--cov-config=pyproject.toml",
    )

@nox.session
def lint(session):
    session.install("black", "ruff")
    session.run("ruff", LIBNAME)
    session.run("black", "--check", LIBNAME)


@nox.session
def typecheck(session):
    session.install("mypy")
    install_dev_requirements(session)
    session.run("mypy", "-p", LIBNAME, "--no-incremental")


@nox.session
def format(session):
    session.install("black", "ruff")
    session.run("ruff", LIBNAME, "--fix")
    session.run("black", LIBNAME)
