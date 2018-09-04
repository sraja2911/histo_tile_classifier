nvidia-docker run \
     -it --rm -p5555:8888 \
     -v "${PWD}:/app:rw" \
     -v "/home/raj/github/histo_tile_classifier:/data/code:rw" \
     -v "/home/raj/github/histo_tile_classifier/results:/data/output/results:rw" \
     -v "/media/raj/Raj1_5/histo_tile_50k_data/train:/data/train:rw" \
     -v "/media/raj/Raj1_5/histo_tile_50k_data/test:/data/test:rw" \
     fgiuste/neuroml:py3
