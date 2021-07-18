# tmd-radar-scraper

## Build docker image

```sh
docker build tmd-radar-scraper -t tmd-radar-scraper
```

## Start container

```sh
docker run -it --rm -v tmd-radar-scraper:/app/data --name tmd-radar-scraper tmd-radar-scraper
```

## View logs

```sh
docker run -it --rm -v tmd-radar-scraper:/data --name tmd-radar-scraper-log ubuntu bash
tail -f /data/main.log
```
