#!/bin/bash
scriptDir="$(dirname "$0")"

# Regenerate computed results (figs) needed for compiling paper
./reproduce/computed.sh

echo '' ; echo 'Reproduce text of paper' ; echo ''

# Reproduce text of paper

# This script may only run on a system on which LaTeX has the ability to write to
# parent directories in the filesystem.
# This is controlled by parameters in the texmf.cnf file:
# 
#    openout_any = a
#    shell_escape = t
#
# Google 'LaTeX write permissions' to determine how to set these on your system
# Or change the output directory from LaTeX to /tmp here and elsewhere in the documents

# Make tikz figures

cd Figures 
for f in InequalityPFGICFHWCRIC RelatePFGICFHWCRICPFFVAC Inequalities; do
    pdflatex --output-format pdf -output-directory=../LaTeX "$f-tikzMake.tex" >/dev/null
    cp       "../LaTeX/$f-tikzMake.pdf" "$f.pdf"
    ebb -x "$f.pdf"
done

cd ..

# Compile LaTeX files in root directory
for file in BufferStockTheory BufferStockTheory-NoAppendix BufferStockTheory-Slides; do
    echo '' ; echo "Compiling $file" ; echo ''
    pdflatex -halt-on-error -output-directory=LaTeX "$file"
    pdflatex -halt-on-error -output-directory=LaTeX "$file"
    bibtex LaTeX/"$file"
    pdflatex -halt-on-error -output-directory=LaTeX "$file"
    pdflatex -halt-on-error -output-directory=LaTeX "$file"
    echo '' ; echo "Compiled $file" ; echo ''
done

# Compile All-Figures and All-Tables
for type in Figures Tables; do
    cmd="pdflatex -halt-on-error -output-directory=LaTeX $type/All-$type"
    echo "$cmd" ; eval "$cmd"
    [[ -e LaTeX/"$type/All-$type" ]] && bibtex LaTeX/"$type/All-$type" && pdflatex -halt-on-error -output-directory=LaTeX "$type/All-$type"
    pdflatex -halt-on-error -output-directory=LaTeX "$type/All-$type"
    mv -f "LaTeX/All-$type.pdf" "$type"  # Move from the LaTeX output directory to the destination
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
rm -f /tmp/appendices economics.bib 
[[ -e BufferStockTheory.pdf ]] && rm -f BufferStockTheory.pdf

echo '' ; echo 'Paper has been compiled to LaTeX/BufferStockTheory.pdf' ; echo ''

