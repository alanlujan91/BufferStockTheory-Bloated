#!/bin/bash
# This script will only run on a system on which LaTeX has the ability to write to
# parent directories in the filesystem.
# This is controlled by parameters in the texmf.cnf file:
# 
#    openout_any = a
#    shell_escape = t
#
# Google 'LaTeX write permissions' to determine how to set these on your system
# Or change the output directory from LaTeX to /tmp here and elsewhere in the documents

scriptDir="$(dirname "$0")"

# Compile LaTeX files in root directory

for file in BufferStockTheory BufferStockTheory-NoAppendix BufferStockTheory-Slides; do
    pdflatex -halt-on-error -output-directory=LaTeX "$file"
    pdflatex -halt-on-error -output-directory=LaTeX "$file"
    bibtex LaTeX/"$file"
    pdflatex -halt-on-error -output-directory=LaTeX "$file"
    pdflatex -halt-on-error -output-directory=LaTeX "$file"
done

# Compile All-Figures and All-Tables
for type in Figures Tables; do
    cmd="pdflatex -halt-on-error -output-directory=LaTeX $type/All-$type"
    echo "$cmd" ; eval "$cmd"
    [[ -e LaTeX/"$type/All-$type" ]] && bibtex LaTeX/"$type/All-$type" && pdflatex -halt-on-error -output-directory=LaTeX "$type/All-$type"
    pdflatex -halt-on-error -output-directory=LaTeX "$type/All-$type"
    mv "LaTeX/All-$type.pdf" "$type"
done

# All the appendices can be compiled as standalone documents (they are "subfiles")
# Make a list of all the appendices:
find ./Appendices -name '*.tex' ! -name '*econtexRoot*' ! -name '*econtexPath*' -maxdepth 1 -exec echo {} \; > /tmp/appendices

# For each such file, process it by pdflatex
# If it contains a standalone bibliography, process that
# Then rerun pdflatex -halt-on-error to complete the processing and move the resulting pdf file

# economics.bib file should be empty (in public repo)
touch economics.bib ; touch Appendices/economics.bib ; touch LaTeX/economics.bib

while read appendixName; do
    filename=$(basename ${appendixName%.*}) # Strip the path and the ".tex"
    cmd="pdflatex -halt-on-error --shell-escape --output-directory=LaTeX $appendixName"
    cmd="pdflatex -halt-on-error --output-directory=LaTeX $appendixName"
    echo "$cmd" ; eval "$cmd"
    if [[ -e "LaTeX/$filename.aux" ]] ; then  # bibfile exists
	bibtex LaTeX/$filename 
	pdflatex -halt-on-error --output-directory=LaTeX $appendixName
    fi
    pdflatex -halt-on-error --output-directory=LaTeX "$appendixName"
    mv "LaTeX/$filename.pdf" Appendices
done < /tmp/appendices

# Cleanup
rm /tmp/appendices economics.bib 
[[ -e BufferStockTheory.pdf ]] && rm -f BufferStockTheory.pdf

# Make a copy of the generated PDF 
cp LaTeX/BufferStockTheory.pdf BufferStockTheory.pdf
