docker run \
     -it --rm -p3333:8888 \
     -v "${PWD}:/app:rw" \
     -v "/home/raj/github/histo_tile_classifier:/data/code:rw" \
     -v "/home/raj/github/histo_tile_classifier/results:/data/output/results:rw" \
     -v "/home/raj/histo_tile_classifier_data:/data/train:rw" \
     fgiuste/histomicstk