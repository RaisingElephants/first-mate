# FirstMate

Find your crowd - FirstMate helps you make friends that work with your schedule.

## Developing

We're using `uv` as a package manager.

### Set up `.env` file for development

Create a file `.env`, with contents adapted from the following

```shell
# Enable dev mode
FIRSTMATE_DEV=true
# Secret used for encrypting session cookie
FIRSTMATE_SECRET="your complex secret"
# Data directory path
FIRSTMATE_DATA="."
```

### Install dependencies

```sh
uv sync
```

### Run type checking

```sh
uv run basedpyright
```

### Run the app

```sh
uv run -m first_mate
```

## Deploying

Easiest with Docker Compose. Data file can't be written unless it was created
before the container starts. I don't know why, and I want to sleep, so I'll
troubleshoot some other time.
