# tmd-radar-scraper

## Build docker image

```sh
docker build https://github.com/ThewApp/tmd-radar-scraper.git#main -t tmd-radar-scraper:main
```

## Usage

Start

```sh
docker run -d --restart always -v tmd-radar-scraper:/app/data --name tmd-radar-scraper tmd-radar-scraper:main
```

Stop

```sh
docker stop tmd-radar-scraper && docker rm tmd-radar-scraper
```

## View logs

```sh
docker run -it --rm -v tmd-radar-scraper:/data --name tmd-radar-scraper-log ubuntu bash
tail -f /data/main.log
```
