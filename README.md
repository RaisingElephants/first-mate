# first-mate

Find yourself some friends on campus at UNSW

## Developing

We're using `uv` as a package manager.

### Set up `.env` file for development

Create a file `.env`, where you set the variable `FIRSTMATE_DEV` to `true`

```shell
FIRSTMATE_DEV=true
```

### Install dependencies

```sh
uv install
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
