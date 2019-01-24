#!/bin/bash
docker run --net=host --rm --mount src="$(pwd)",target=/app,type=bind -it steam_scraper $*
