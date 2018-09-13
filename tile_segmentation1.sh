nvidia-docker run \
     -it --rm -p4444:8888 \
     -v "${PWD}:/app:rw" \
     -v "/home/raj/github/histo_tile_classifier:/data/code:rw" \
     -v "/home/raj/github/histo_tile_classifier/results:/data/output/results:rw" \
     -v "/media/raj/Raj1_5/5k_tiles_data/train:/data/train:rw" \
     -v "/media/raj/Raj1_5/5k_tiles_data/test:/data/test:rw" \
     fgiuste/histomicstk