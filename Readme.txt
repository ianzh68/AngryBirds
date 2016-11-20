{\rtf1\ansi\ansicpg1252\cocoartf1404\cocoasubrtf130
{\fonttbl\f0\fswiss\fcharset0 Helvetica;}
{\colortbl;\red255\green255\blue255;}
\margl1440\margr1440\vieww11740\viewh9100\viewkind0
\pard\tx720\tx1440\tx2160\tx2880\tx3600\tx4320\tx5040\tx5760\tx6480\tx7200\tx7920\tx8640\pardirnatural\partightenfactor0

\f0\fs24 \cf0 Hi, this is my term project for 15-112 Fundamental of Programming and Computer Science in CMU, my project is a recreation (with some new features) of the game Angry Birds, please follow the game built-in instructions to play, have fun!\
\
\pard\tx720\tx1440\tx2160\tx2880\tx3600\tx4320\tx5040\tx5760\tx6480\tx7200\tx7920\tx8640\pardirnatural\partightenfactor0
\cf0 And a few things to notice:\
\
1. To launch the game, please run the file \'93run.py\'94 in the folder \'93tp3\'94.\
\
2. The environment I develop this game is Mac OS X El Captain, it may not work well on Windows OS, if it crashes because of warnings about \'93chipmunk\'94, please visit this page for solution (see \'93Compile Chipmunk\'94 at bottom): {\field{\*\fldinst{HYPERLINK "http://www.pymunk.org/en/latest/installation.html"}}{\fldrslt http://www.pymunk.org/en/latest/installation.html}}.\
\
3. I utilized a third party library called \'93pymunk\'94, it was already included in this file. Besides that, you will still need pygame to run the code, I am sorry that I am NOT able to include it here. If you don\'92t have it on your computer, please install pygame before you run it by following: {\field{\*\fldinst{HYPERLINK "http://florian-berger.de/en/articles/installing-pygame-for-python-3-on-os-x/"}}{\fldrslt http://florian-berger.de/en/articles/installing-pygame-for-python-3-on-os-x/}}.\
\
4. If it crashes because of error \'93pygame.error: Unrecognized music format\'94 on Mac OS X: this is probably because you don\'92t have sdl_mixer installed properly in your computer, if you have brew installed already, try following steps:\
\
(if not: install brew first: {\field{\*\fldinst{HYPERLINK "http://brew.sh/"}}{\fldrslt http://brew.sh/}}, then follow the steps below)\
\
	brew install libvorbis\
	brew reinstall dl_mixer\
\
and see if that works, if not, try:\
\
	brew uninstall libvorbis libogg\
	brew reinstall dl_mixer \'97with-libvorbis\
\
It should work now.\
(solution from {\field{\*\fldinst{HYPERLINK "https://github.com/justinmeister/Mario-Level-1/issues/5"}}{\fldrslt https://github.com/justinmeister/Mario-Level-1/issues/5}})\
\
5. Now you are good to go, have fun!\
\
}