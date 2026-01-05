#!/bin/bash

cd "$(dirname "$0")"

echo "Compiling LaTeX presentation..."
pdflatex -interaction=nonstopmode academic_presentation.tex

if [ -f academic_presentation.pdf ]; then
    echo "✓ Success! PDF created: academic_presentation.pdf"
    ls -lh academic_presentation.pdf
else
    echo "✗ Compilation failed. Check academic_presentation.log for errors"
    tail -50 academic_presentation.log
fi
