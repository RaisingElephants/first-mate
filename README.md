# first-mate

Find yourself some friends on campus at UNSW

## Developing

We're using `uv` as a package manager.

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
uv run -m first-mate
```

### Serve the directory of test calendars

```sh
python -m http.server -d test_calendars -b 127.0.0.1
```
