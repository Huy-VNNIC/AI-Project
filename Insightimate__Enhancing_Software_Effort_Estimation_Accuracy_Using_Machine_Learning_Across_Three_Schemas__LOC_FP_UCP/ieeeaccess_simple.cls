\LoadClass{IEEEtran}

\RequirePackage{ifpdf}
\RequirePackage{xkeyval}

\newif\iflineno\linenofalse
\newif\ifaccesseditors\accesseditorsfalse

\DeclareOption{accesseditors}{\accesseditorstrue}
\DeclareOption{lineno}{\linenotrue}
\DeclareOption{nolineno}{\linenofalse}

\ExecuteOptions{a4paper,10pt,twocolumn,twoside,lineno,journal}
\ProcessOptions

\def\BibTeX{{\rm B\kern-.05em{\sc i\kern-.025em b}\kern-.08em
    T\kern-.1667em\lower.7ex\hbox{E}\kern-.125emX}}

% Simple font setup without special fonts
\makeatletter

\def\titlefont{\bfseries\Large}
\def\authorfont{\normalsize}
\def\addressfont{\small}
\def\abstractfont{\normalsize}

\newcommand\history[1]{\gdef\@history{#1}}
\newcommand\doi[1]{\gdef\@doi{#1}}

\newcommand\address[2][]{\gdef\@address{#2}}
\newcommand\tfootnote[1]{\gdef\@tfootnote{#1}}
\newcommand\corresp[1]{\gdef\@corresp{#1}}

\newcommand\authorrefmark[1]{\textsuperscript{#1}}

\def\@history{}
\def\@doi{}
\def\@address{}
\def\@tfootnote{}
\def\@corresp{}

\makeatother
