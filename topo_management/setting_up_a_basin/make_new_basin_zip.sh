#!/bin/bash
cd new_basin && \
zip ../new_basin.zip Makefile \
                  pour_points.bna \
                  scripts/*/* \
                  dem_sources.txt \
                  docker-compose.yml \
