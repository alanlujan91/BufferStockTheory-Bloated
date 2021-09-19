#!/bin/bash
scriptDir="$(dirname "$0")"

# Regenerate computed results (figs) needed for compiling paper
./reproduce/computed.sh

echo '' ; echo 'Reproduce text of paper' ; echo ''

output_directory='LaTeX'

# Make tikz figures
cd Figures 
for f in InequalityPFGICFHWCRIC RelatePFGICFHWCRICPFFVAC Inequalities; do
    pdflatex --output-format pdf -output-directory="../$output_directory" "$f-tikzMake.tex" >/dev/null
    mv -f                                          "../$output_directory/$f-tikzMake.pdf" "$f.pdf"
done
cd ..

# Make sure bib resources are available 
if [[ ! -s "$file.bib" ]]; then  # $file.bib exists and is not empty
    # economics.bib files should exist if they do not yet 
    for dir in . Appendices Figures Tables LaTeX Resources/LaTeXInputs; do
	touch "$dir/economics.bib"
    done
fi

# Compile LaTeX files in root directory
for file in BufferStockTheory BufferStockTheory-NoAppendix BufferStockTheory-Slides; do
    echo '' ; echo "Compiling $file" ; echo ''
    pdflatex -halt-on-error -output-directory=$output_directory "$file"
    pdflatex -halt-on-error -output-directory=$output_directory "$file" > /dev/null
    bibtex $output_directory/"$file"
    pdflatex -halt-on-error -output-directory=$output_directory "$file" > /dev/null
    pdflatex -halt-on-error -output-directory=$output_directory "$file"
    echo '' ; echo "Compiled $file" ; echo ''
done

# Compile All-Figures and All-Tables
for type in Figures Tables; do
    cmd="pdflatex -halt-on-error -output-directory=$output_directory $type/All-$type"
    echo "$cmd" ; eval "$cmd"
    # If there is a .bib file, make the references
    [[ -e "../$output_directory/$type/All-$type.aux" ]] && bibtex "$type/All-$type.bib" && eval "$cmd" && eval "$cmd" 
    mv -f "$output_directory/All-$type.pdf" "$type"  # Move from the LaTeX output directory to the destination
done

# All the appendices can be compiled as standalone documents (they are "subfiles")
# Make a list of all the appendices:
find ./Appendices -name '*.tex' ! -name '*econtexRoot*' ! -name '*econtexPath*' -maxdepth 1 -exec echo {} \; > /tmp/appendices

# For each appendix process it by pdflatex
# If it contains a standalone bibliography, process that
# Then rerun pdflatex to complete the processing and move the resulting pdf file

while read appendixName; do
    filename=$(basename ${appendixName%.*}) # Strip the path and the ".tex"
    #    cmd="pdflatex -halt-on-error --shell-escape --output-directory=$output_directory $appendixName"
    cmd="pdflatex -halt-on-error                 --output-directory=$output_directory $appendixName"
    echo "$cmd" ; eval "$cmd"
    if grep -q 'bibliography{' "$appendixName"; then
	bibtex $output_directory/$filename 
	eval "$cmd"
    fi
    eval "$cmd"
    mv "$output_directory/$filename.pdf" Appendices
done < /tmp/appendices

# Cleanup
rm -f /tmp/appendices economics.bib 
[[ -e BufferStockTheory.pdf ]] && rm -f BufferStockTheory.pdf

echo '' ; echo "Paper has been compiled to $output_directory/BufferStockTheory.pdf" ; echo ''

