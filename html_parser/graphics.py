import sys
import subprocess
import os
import base64
import json

output_directory = "./output"
output_latex_filename = output_directory + "/interpreted_webpage_Odrzywolek_Szewczyk"

# The example image output requires these packages:
# pdflatex

outfile = None
logfile = None

image_start = "BEGIN_IMAGE_f9825uweof8jw9fj4r8"
image_end = "END_IMAGE_0238jfw08fjsiufhw8frs"


def output_image(name, _format, _bytes):
    data = {'name': name, 'format': _format, 'bytes': base64.encodestring(_bytes)}

    sys.stdout.write(image_start)
    sys.stdout.write(json.dumps(data))
    sys.stdout.write(image_end)


def word(x):
    global outfile
    for i in range(len(x)):
        if x[i] == '_':
            outfile.write("\_")
        elif x[i] != '\\':
            outfile.write(x[i])
    outfile.write(" ")


def warning(x):
    global outfile
    outfile.write("{\\color{red}{\\bf{" + x + "}}}")


closetags = []


def pushclosing(x):
    global closetags
    closetags = [x] + closetags


def begintag(tag, args):
    global outfile
    global logfile
    tag = tag.lower()
    # need "IMG"
    logfile.write("TAG + " + tag + "\n")
    if tag == "a":
        is_href_found = False
        for arg in args:
            if arg[0] == "Attribute" and arg[1] == "href":
                is_href_found = True
                target = arg[2]
                outfile.write("\\href{" + target + r"}{\underline{")
                pushclosing("}}")
        if not is_href_found:
            warning("invalid 'a' tag: no 'href' argument")
            pushclosing("")
    elif tag == "b" or tag == "strong":
        outfile.write("\\textbf{")
        pushclosing("}")
    elif tag == "ul":
        outfile.write("\\begin{itemize}")
        pushclosing("\\end{itemize}")
    elif tag == "ol":
        outfile.write("\\begin{enumerate}")
        pushclosing("\\end{enumerate}")
    elif tag == "li":
        outfile.write("\\item{")
        pushclosing("}")
    elif tag == "big":
        outfile.write("{\\Large ")
        pushclosing("}")
    elif tag == "tt" or tag == "code":
        outfile.write("{\\tt ")
        pushclosing("}")
    elif tag == "small":
        outfile.write("{\\footnotesize ")
        pushclosing("}")
    elif tag == "i" or tag == "em":
        outfile.write("\\emph{")
        pushclosing("}")
    elif tag == "hr":
        outfile.write("{\\begin{center} \\line(1,0){400} \\end{center}}")
        pushclosing("")
    elif tag == "h1":
        outfile.write("\\section*{")
        pushclosing("}")
    elif tag == "h2":
        outfile.write("\\subsection*{")
        pushclosing("}")
    elif tag == "h3":
        outfile.write("\\subsubsection*{")
        pushclosing("}")
    elif tag == "p" or tag == "br":
        outfile.write("\n~\n\n\\noindent ")
        pushclosing("\n")
    else:
        pushclosing("")


def endtag():
    global outfile
    global logfile
    global closetags
    if not closetags:
        raise IndexError
    tag = closetags[0]
    closetags = closetags[1:]
    logfile.write("TAG -\n")
    outfile.write(tag)


def initialize():
    global outfile
    global logfile
    global output_latex_filename
    os.makedirs(os.path.dirname(output_latex_filename), exist_ok=True)
    outfile = open(output_latex_filename + ".tex", 'w+')
    logfile = open(output_latex_filename + ".taglog", 'w+')
    outfile.write("""
\\documentclass{article}
\\usepackage{hyperref}
\\hypersetup{
  colorlinks,%
    citecolor=blue,%
    filecolor=blue,%
    linkcolor=blue,%
    urlcolor=blue
}
\\usepackage{graphicx}
\\usepackage{color}
\\usepackage{url}
\\pagestyle{empty}
\\begin{document}
""")


def finalize():
    global outfile
    global logfile
    logfile.close()
    outfile.write("""
\\end{document}
""")
    print("Writing TEX Output: " + output_latex_filename + ".tex")
    outfile.close()
    print("Rendering PDF Graphics: " + output_latex_filename + ".pdf")
    cmd = "pdflatex -output-directory " + output_directory + " " + output_latex_filename + ".tex > /dev/null < /dev/null"
    subprocess.call(cmd, shell=True)