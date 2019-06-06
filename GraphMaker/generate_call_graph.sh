#!/usr/bin/env bash

# brew install graphviz
# git clone https://github.com/davidfraser/pyan.git 

#pyan jointjs2dot.py -e --uses --no-defines \
#        --colored --grouped --annotated --dot > jointjs2dot.dot


filename="$1"
filename_pattern="${filename%.bar}"
filename_no_ext="${filename_pattern##*/}"

dest_path="call_graphs"

mkdir -p "${dest_path}"

dest_file_path=${dest_path}/${filename}
dest_file_no_ext_path=${dest_path}/${filename_no_ext}

for rank in 'TB' 'LR' 'BT' 'RL'; do

    echo "dest_file_path: ${dest_file_path}"
    echo "dest_file_no_ext_path: ${dest_file_no_ext_path}"

    pyan "${filename}" -e --uses  \
            --dot-rankdir=${rank} --colored -G --grouped --annotated --dot > ${dest_file_no_ext_path}-${rank}.dot

    dot -Tsvg ${dest_file_no_ext_path}-${rank}.dot > ${dest_file_no_ext_path}-${rank}.svg

done

pyan "${filename}" -e --uses  \
            --colored -G --grouped --annotated --dot > ${dest_file_no_ext_path}.dot

dot -Tsvg ${dest_file_no_ext_path}.dot > ${dest_file_no_ext_path}.svg