#!/usr/bin/env python2
# coding=utf8
# version: 0.8.1

version = "0.8.1"
projectName = "Omega Fonts"
projectNameAbbreviation = "OMF"
projectNameSingular = projectName[:-1]
# Credit to Nerd Fonts (https://github.com/ryanoasis/nerd-fonts)"
# 
#
# usage:
#
#
#
# & 'C:\Program Files (x86)\FontForgeBuilds\bin\fontforge.exe' -script font-patcher --windows --powerline --octicons -out C:\Users\ehiller\dev\fonts-out\ C:\Users\ehiller\dev\fonts-in\SourceSansPro-BoldItalic.ttf


import sys

try:
    import psMat
except ImportError:
    sys.stderr.write(projectName + ": FontForge module is probably not installed. [See: http://designwithfontforge.com/en-US/Installing_Fontforge.html]\n")
    sys.exit(1)

import re
import os
import argparse
import errno

try:
    #Load the module
    import fontforge

except ImportError:
    sys.stderr.write(projectName + ": FontForge module could not be loaded. Try installing fontforge python bindings [e.g. on Linux Debian or Ubuntu: `sudo apt-get install fontforge python-fontforge`]\n")
    sys.exit(1)

# argparse stuff

parser = argparse.ArgumentParser(description='Patches a given font with programming and web development related glyphs (mainly for https://github.com/ryanoasis/vim-devicons)')
parser.add_argument('-v', '--version', action='version', version=projectName + ": %(prog)s ("+version+")")
parser.add_argument('font', help='The path to the font to be patched (e.g. Inconsolata.otf)')
parser.add_argument('-s', '--use-single-width-glyphs', dest='single', action='store_true', help='Whether to generate the glyphs as single-width not double-width (default is double-width)', default=False)
parser.add_argument('-q', '--quiet', '--shutup', dest='quiet', action='store_true', help='Do not generate verbose output', default=False)
parser.add_argument('-w', '--windows', '--limit-font-name-length', dest='windows', action='store_true', help='Limit the internal font name to a maximum of 31 characters (for safe Windows compatiblity)', default=False)
parser.add_argument('--fontawesome', dest='fontawesome', action='store_true', help='Add Font Awesome Glyphs (http://fortawesome.github.io/Font-Awesome)', default=False)
parser.add_argument('--fontlinux', dest='fontlinux', action='store_true', help='Add Font Linux Glyphs (https://github.com/Lukas-W/font-linux)', default=False)
parser.add_argument('--octicons', dest='octicons', action='store_true', help='Add Octicons Glyphs (https://octicons.github.com)', default=False)
parser.add_argument('--pomicons', dest='pomicons', action='store_true', help='Add Pomicon Glyphs (https://github.com/gabrielelana/pomicons)', default=False)
parser.add_argument('--powerline', dest='powerline', action='store_true', help='Add Powerline Glyphs', default=False)
parser.add_argument('--powerlineextra', dest='powerlineextra', action='store_true', help='Add Powerline Glyphs (https://github.com/ryanoasis/powerline-extra-symbols)', default=False)
parser.add_argument('--careful', dest='careful', action='store_true', help='Do not overwrite existing glyphs if detected', default=False)
parser.add_argument('-out', '--outputdir', type=str, nargs='?', dest='outputdir', help='The directory to output the patched font file to', default=".")
args = parser.parse_args()


#changelog = open("changelog.md", "r")
minimumVersion = 20141231
actualVersion = int(fontforge.version())
# un-comment following line for testing invalid version error handling
#actualVersion = 20120731
# versions tested: 20150612, 20150824

if actualVersion < minimumVersion:
    print projectName + ": You seem to be using an unsupported (old) version of fontforge: " + str(actualVersion)
    print projectName + ": Please use at least version: " + str(minimumVersion)
    sys.exit(1)


verboseAdditionalFontNameSuffix = " " + projectNameSingular

if args.windows:
    # attempt to shorten here on the additional name BEFORE trimming later
    additionalFontNameSuffix = " " + projectNameAbbreviation
else:
    additionalFontNameSuffix = verboseAdditionalFontNameSuffix

if args.fontawesome:
    additionalFontNameSuffix += " Plus Font Awesome"
    verboseAdditionalFontNameSuffix += " Plus Font Awesome"

if args.octicons:
    additionalFontNameSuffix += " Plus Octicons"
    verboseAdditionalFontNameSuffix += " Plus Octicons"

if args.pomicons:
    additionalFontNameSuffix += " Plus Pomicons"
    verboseAdditionalFontNameSuffix += " Plus Pomicons"

if args.fontlinux:
    additionalFontNameSuffix += " Plus Font Linux"
    verboseAdditionalFontNameSuffix += " Plus Font Linux"

# if all source glyphs included simplify the name
if args.fontawesome and args.octicons and args.pomicons and args.powerlineextra and args.fontlinux:
    additionalFontNameSuffix = " " + projectNameSingular + " Complete"
    verboseAdditionalFontNameSuffix = " " + projectNameSingular + " Complete"

# add mono signifier to end of name
if args.single:
    additionalFontNameSuffix += " Mono"
    verboseAdditionalFontNameSuffix += " Mono"

sourceFont = fontforge.open(args.font)

# basically split the font name around the dash "-" to get the fontname and the style (e.g. Bold)
# this does not seem very reliable so only use the style here as a fallback if the font does not
# have an internal style defined (in sfnt_names)
# using '([^-]*?)' to get the item before the first dash "-"
# using '([^-]*(?!.*-))' to get the item after the last dash "-"
fontname, fallbackStyle = re.match("^([^-]*).*?([^-]*(?!.*-))$", sourceFont.fontname).groups()
# dont trust 'sourceFont.familyname'
familyname = fontname
# fullname (filename) can always use long/verbose font name, even in windows
fullname = sourceFont.fullname + verboseAdditionalFontNameSuffix
fontname = fontname + additionalFontNameSuffix.replace(" ", "")

# let us try to get the 'style' from the font info in sfnt_names and fallback to the
# parse fontname if it fails:
try:
    # search tuple:
    subFamilyTupleIndex = [x[1] for x in sourceFont.sfnt_names].index("SubFamily")
    # String ID is at the second index in the Tuple lists
    sfntNamesStringIDIndex = 2
    # now we have the correct item:
    subFamily = sourceFont.sfnt_names[sfntNamesStringIDIndex][subFamilyTupleIndex]
except IndexError:
    print projectName + ": Could not find 'SubFamily' for given font, falling back to parsed fontname"
    subFamily = fallbackStyle

# some fonts have inaccurate 'SubFamily', if it is Regular let us trust the filename more:
if subFamily == "Regular":
    subFamily = fallbackStyle

fontname += " - " + subFamily

if args.windows:
    maxLength = 31
    familyname += " " + projectNameAbbreviation
    fullname += " Windows Compatible"
    # now make sure less than 32 characters name length
    #if len(fullname) > maxLength:
    #    fullname = fullname[:maxLength]
    if len(fontname) > maxLength:
        fontname = fontname[:maxLength]
    if len(fullname) > maxLength:
        familyname = familyname[:maxLength]
else:
    familyname += " " + projectNameSingular

# rename font

def replace_all(text, dic):
    for i, j in dic.iteritems():
        text = text.replace(i, j)
    return text


def make_sure_path_exists(path):
    try:
        os.makedirs(path)
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raisee

make_sure_path_exists(args.outputdir)

# comply with SIL Open Font License (OFL)
reservedFontNameReplacements = { 'source': 'sauce', 'Source': 'Sauce', 'hermit': 'hurmit', 'Hermit': 'Hurmit', 'fira': 'fura', 'Fira': 'Fura', 'hack': 'knack', 'Hack': 'Knack' }

projectInfo = "Patched with '" + projectName + " Patcher' (https://github.com/ryanoasis/nerd-fonts)"

sourceFont.familyname = replace_all(familyname, reservedFontNameReplacements)
sourceFont.fullname = replace_all(fullname, reservedFontNameReplacements)
sourceFont.fontname = replace_all(fontname, reservedFontNameReplacements)
sourceFont.appendSFNTName('English (US)', 'Preferred Family', sourceFont.familyname)
sourceFont.appendSFNTName('English (US)', 'Compatible Full', sourceFont.fullname)
sourceFont.appendSFNTName('English (US)', 'SubFamily', subFamily)
sourceFont.comment = projectInfo
#sourceFont.fontlog = projectInfo + "\n\n" + changelog.read()

# todo version not being set for all font types (e.g. ttf)
#print "Version was " + sourceFont.version
sourceFont.version += ";" + projectName + " " + version
#print "Version now is " + sourceFont.version

# glyph font

sourceFont_em_original = sourceFont.em

# Open fonts and force the em size to be equal

#symbols = fontforge.open("glyph-source-fonts/original-source.otf")
powerlineSymbols = fontforge.open("glyph-source-fonts/PowerlineSymbols.otf")
#powerlineExtraSymbols = fontforge.open("glyph-source-fonts/PowerlineExtraSymbols.otf")
#symbolsDevicons = fontforge.open("glyph-source-fonts/devicons.ttf")

#symbols.em = sourceFont.em
#symbolsDevicons.em = sourceFont.em
# powerlineExtraSymbols.em = sourceFont.em

if args.fontawesome:
    fontawesome = fontforge.open("glyph-source-fonts/FontAwesome.otf")
    fontawesome.em = sourceFont.em

if args.octicons:
    octicons = fontforge.open("glyph-source-fonts/octicons.ttf")
    octicons.em = sourceFont.em
    octiconsExactEncodingPosition = True

if args.pomicons:
    pomicons = fontforge.open("glyph-source-fonts/Pomicons.otf")
    pomicons.em = sourceFont.em

if args.fontlinux:
    fontlinux = fontforge.open("glyph-source-fonts/font-linux.ttf")
    fontlinux.em = sourceFont.em
    fontlinuxExactEncodingPosition = True

# Prevent glyph encoding position conflicts between glyph sets

if args.fontawesome and args.octicons:
    octiconsExactEncodingPosition = False

if args.fontawesome or args.octicons:
    fontlinuxExactEncodingPosition = False

# Define the character ranges

# Symbol font ranges
symbolsPomiconsRangeStart = 0xE000
symbolsPomiconsRangeEnd = 0xE00A

symbolsPowerlineRange1Start = 0xE0A0
symbolsPowerlineRange1End = 0xE0A2

symbolsPowerlineRange2Start = 0xE0B0
symbolsPowerlineRange2End = 0xE0B3

symbolsPowerlineExtraRange1Start = 0xE0A3
symbolsPowerlineExtraRange1End = 0xE0A3

symbolsPowerlineExtraRange2Start = 0xE0B4
symbolsPowerlineExtraRange2End = 0xE0C8

symbolsPowerlineExtraRange3Start = 0xE0CC
symbolsPowerlineExtraRange3End = 0xE0D4

symbolsOriginalRangeStart = 0xE4FA
symbolsOriginalRangeEnd = 0xE52A

symbolsDeviconsRangeStart = 0xE600
symbolsDeviconsRangeEnd = 0xE6C5

symbolsFontAwesomeRangeStart = 0xF000
symbolsFontAwesomeRangeEnd = 0xF295

symbolsOcticonsRangeStart = 0x26A1
symbolsOcticonsRangeEnd = 0xF0DB

symbolsFontLinuxRangeStart = 0xF100
symbolsFontLinuxRangeEnd = 0xF115

# Destination font ranges
sourceFontPomiconsStart = 0xE000
sourceFontPomiconsEnd = 0xE00A

sourceFontOriginalStart = 0xE5FA
sourceFontOriginalEnd = 0xE62A

sourceFontDeviconsStart = 0xE700
sourceFontDeviconsEnd = 0xE7C5

sourceFontFontAwesomeStart = 0xF000
sourceFontFontAwesomeEnd = 0xF295

sourceFontOcticonsStart = 0xF400
sourceFontOcticonsEnd = 0xF4DB

sourceFontFontLinuxStart = 0xF300
sourceFontFontLinuxEnd = 0xF315


SYM_ATTR = {
	# Right/left-aligned glyphs will have their advance width reduced in order to overlap the next glyph slightly
	0x2b60: { 'align': 'c', 'stretch': 'y' , 'overlap': False },
	0x2b61: { 'align': 'c', 'stretch': ''  , 'overlap': False },
	0x2b62: { 'align': 'r', 'stretch': ''  , 'overlap': False },
	0x2b63: { 'align': 'l', 'stretch': ''  , 'overlap': False },
	0x2b64: { 'align': 'c', 'stretch': ''  , 'overlap': False },
	0x2b80: { 'align': 'l', 'stretch': 'xy', 'overlap': True  },
	0x2b81: { 'align': 'l', 'stretch': 'xy', 'overlap': True  },
	0x2b82: { 'align': 'r', 'stretch': 'xy', 'overlap': True  },
	0x2b83: { 'align': 'r', 'stretch': 'xy', 'overlap': True  },
}


# Initial font dimensions
font_dim = {
	'xmin'  :    0,
	'ymin'  :    -sourceFont.descent,
	'xmax'  :    0,
	'ymax'  :    sourceFont.ascent,
	'width' :    0,
	'height':    0,
}

# Find the biggest char width and height
#
# 0x00-0x17f is the Latin Extended-A range
# 0x2500-0x2600 is the box drawing range
for glyph in range(0x00, 0x17f) + range(0x2500, 0x2600):
	try:
		(xmin, ymin, xmax, ymax) = sourceFont[glyph].boundingBox()
	except TypeError:
		continue

	if font_dim['width'] == 0:
		font_dim['width'] = sourceFont[glyph].width

	if ymin < font_dim['ymin']: font_dim['ymin'] = ymin
	if ymax > font_dim['ymax']: font_dim['ymax'] = ymax
	if xmax > font_dim['xmax']: font_dim['xmax'] = xmax

# Calculate font height
font_dim['height'] = abs(font_dim['ymin']) + font_dim['ymax']

# Update the font encoding to ensure that the Unicode glyphs are available
sourceFont.encoding = 'ISO10646'

# Fetch this property before adding outlines
onlybitmaps = sourceFont.onlybitmaps

def get_dim(glyph):
	bbox = glyph.boundingBox()

	return  {
		'xmin'  : bbox[0],
		'ymin'  : bbox[1],
		'xmax'  : bbox[2],
		'ymax'  : bbox[3],

		'width' : bbox[2] + (-bbox[0]),
		'height': bbox[3] + (-bbox[1]),
	}


def copy_glyphs(sourceFont, sourceFontStart, sourceFontEnd, symbolFont, symbolFontStart, symbolFontEnd, exactEncoding=False):

    if exactEncoding is False:
        sourceFontList = []
        sourceFontCounter = 0

        for i in xrange(sourceFontStart, sourceFontEnd + 1):
            sourceFontList.append(format(i, 'X'))

    # Create glyphs from symbol font

    symbolFont.selection.select(("ranges","unicode"),symbolFontStart,symbolFontEnd)
    sourceFont.selection.select(("ranges","unicode"),sourceFontStart,sourceFontEnd)

    for sym_glyph in symbolFont.selection.byGlyphs:

            #sym_attr = SYM_ATTR[sym_glyph.unicode]
            glyphName = sym_glyph.glyphname

            if exactEncoding:
                # use the exact same hex values for the source font as for the symbol font
                currentSourceFontGlyph = sym_glyph.encoding
                copiedToSlot = str(sym_glyph.unicode)
            else:
                # use source font defined hex values based on passed in start and end
                # convince that this string really is a hex:
                currentSourceFontGlyph = int("0x" + sourceFontList[sourceFontCounter], 16)
                copiedToSlot = sourceFontList[sourceFontCounter]

            if args.quiet == False:
                print "updating glyph: " + str(sym_glyph) + " " + str(sym_glyph.glyphname) + " putting at: " + str(copiedToSlot)

            # Prepare symbol glyph dimensions
            sym_dim = get_dim(sym_glyph)

            # Select and copy symbol from its encoding point
            symbolFont.selection.select(sym_glyph.encoding)
            symbolFont.copy()

            # check it
            if args.careful:

                if copiedToSlot.startswith("uni"):
                    copiedToSlot = copiedToSlot[3:]

                codepoint = int("0x" + copiedToSlot, 16)
                try:
                    sourceFont[codepoint]
                except TypeError:
                    # nothing there go ahead and paste at this codepoint
                    sourceFont.selection.select(currentSourceFontGlyph)
                    sourceFont.paste()
            else:
                sourceFont.selection.select(currentSourceFontGlyph)
                sourceFont.paste()

            sourceFont[currentSourceFontGlyph].glyphname = glyphName

            if args.single:
                # Now that we have copy/pasted the glyph, it's time to scale and move it

                # Handle glyph stretching
                #if 'x' in sym_attr['stretch']:
                #        # Stretch the glyph horizontally
                #        scale_ratio = font_dim['width'] / sym_dim['width']

                #        sourceFont.transform(psMat.scale(scale_ratio, 1))
                #if 'y' in sym_attr['stretch']:
                #        # Stretch the glyph vertically
                #        scale_ratio = font_dim['height'] / sym_dim['height']

                #        sourceFont.transform(psMat.scale(1, scale_ratio))

                # Use the dimensions from the pasted and stretched glyph
                sym_dim = get_dim(sourceFont[currentSourceFontGlyph])

                # Center-align the glyph vertically
                font_ycenter = font_dim['height'] / 2
                sym_ycenter  = sym_dim['height'] / 2

                # First move it to the ymax (top)
                sourceFont.transform(psMat.translate(0, font_dim['ymax'] - sym_dim['ymax']))

                # Then move it the y center difference
                sourceFont.transform(psMat.translate(0, sym_ycenter - font_ycenter))

                # Ensure that the glyph doesn't extend outside the font's bounding box
                if sym_dim['width'] > font_dim['width']:
                        # The glyph is too wide, scale it down to fit
                        scale_matrix = psMat.scale(font_dim['width'] / sym_dim['width'], 1)

                        sourceFont.transform(scale_matrix)

                        # Use the dimensions from the stretched glyph
                        sym_dim = get_dim(sourceFont[currentSourceFontGlyph])

                # Handle glyph alignment
                #if sym_attr['align'] == 'c':
                #        # Center align
                #        align_matrix = psMat.translate(font_dim['width'] / 2 - sym_dim['width'] / 2 , 0)
                align_matrix = psMat.translate(font_dim['width'] / 2 - sym_dim['width'] / 2 , 0)
                #elif sym_attr['align'] == 'r':
                #        # Right align
                #        align_matrix = psMat.translate(font_dim['width'] - sym_dim['width'], 0)
                #else:
                        # No alignment (left alignment)
                        #align_matrix = psMat.translate(0, 0)

                sourceFont.transform(align_matrix)

                #if sym_attr['overlap'] is True:
                #        overlap_width = sourceFont.em / 48

                #        # Stretch the glyph slightly horizontally if it should overlap
                #        sourceFont.transform(psMat.scale((sym_dim['width'] + overlap_width) / sym_dim['width'], 1))

                #        if sym_attr['align'] == 'l':
                #                # The glyph should be left-aligned, so it must be moved overlap_width to the left
                #                # This only applies to left-aligned glyphs because the glyph is scaled to the right
                #                sourceFont.transform(psMat.translate(-overlap_width, 0))

                # Ensure the font is considered monospaced on Windows
                sourceFont[currentSourceFontGlyph].width = font_dim['width']

            if exactEncoding is False:
                sourceFontCounter += 1

            # reset selection so iteration works propertly @todo fix? rookie misunderstanding?
            symbolFont.selection.select(("ranges","unicode"),symbolFontStart,symbolFontEnd)
    # end for
    return


#copy_glyphs(sourceFont, sourceFontOriginalStart, sourceFontOriginalEnd, symbols, symbolsOriginalRangeStart, symbolsOriginalRangeEnd)
#copy_glyphs(sourceFont, sourceFontDeviconsStart, sourceFontDeviconsEnd, symbolsDevicons, symbolsDeviconsRangeStart, symbolsDeviconsRangeEnd)


#consola_bold = fontforge.open("fonts-src/consolas_6/consolab.ttf")
#consola_bold = fontforge.open("fonts-src/Hack-v2_020-ttf/Hack-Bold.ttf")
#consola_bold = fontforge.open("fonts-src/dejavu-fonts-ttf-2.37/ttf/DejaVuSansMono-Bold.ttf")
#consola_bold.em = sourceFont.em
#omegaChar = 0x03a9 # a9 is OMEGA , b1 is alpha
#copy_glyphs(sourceFont,omegaChar,omegaChar,consola_bold, omegaChar,omegaChar, True )

if args.powerline:
    copy_glyphs(sourceFont, symbolsPowerlineRange1Start, symbolsPowerlineRange1End, powerlineSymbols, symbolsPowerlineRange1Start, symbolsPowerlineRange1End)
    copy_glyphs(sourceFont, symbolsPowerlineRange2Start, symbolsPowerlineRange2End, powerlineSymbols, symbolsPowerlineRange2Start, symbolsPowerlineRange2End)

if args.powerlineextra:
    copy_glyphs(sourceFont, symbolsPowerlineExtraRange1Start, symbolsPowerlineExtraRange1End, powerlineExtraSymbols, symbolsPowerlineExtraRange1Start, symbolsPowerlineExtraRange1End, True)
    copy_glyphs(sourceFont, symbolsPowerlineExtraRange2Start, symbolsPowerlineExtraRange2End, powerlineExtraSymbols, symbolsPowerlineExtraRange2Start, symbolsPowerlineExtraRange2End, True)
    copy_glyphs(sourceFont, symbolsPowerlineExtraRange3Start, symbolsPowerlineExtraRange3End, powerlineExtraSymbols, symbolsPowerlineExtraRange3Start, symbolsPowerlineExtraRange3End, True)

if args.fontawesome:
    copy_glyphs(sourceFont, sourceFontFontAwesomeStart, sourceFontFontAwesomeEnd, fontawesome, symbolsFontAwesomeRangeStart, symbolsFontAwesomeRangeEnd, True)

if args.octicons:
    copy_glyphs(sourceFont, sourceFontOcticonsStart, sourceFontOcticonsEnd, octicons, symbolsOcticonsRangeStart, symbolsOcticonsRangeEnd, octiconsExactEncodingPosition)

if args.pomicons:
    copy_glyphs(sourceFont, sourceFontPomiconsStart, sourceFontPomiconsEnd, pomicons, symbolsPomiconsRangeStart, symbolsPomiconsRangeEnd)

if args.fontlinux:
    copy_glyphs(sourceFont, sourceFontFontLinuxStart, sourceFontFontLinuxEnd, fontlinux, symbolsFontLinuxRangeStart, symbolsFontLinuxRangeEnd, fontlinuxExactEncodingPosition)

extension = os.path.splitext(sourceFont.path)[1]

# the `PfEd-comments` flag is required for Fontforge to save
# '.comment' and '.fontlog'.
sourceFont.generate(args.outputdir + "/" + sourceFont.fullname + extension, flags=('opentype', 'PfEd-comments'))

print "Generated"
print sourceFont.fullname

