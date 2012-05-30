#!/usr/bin/python
"""
Check the given file for conformance with the hOCR format spec
"""

import sys
import getopt

from lxml.html import parse


################################################################
### misc library code
################################################################
def assoc(key, llist):
    """
    Assoc
    """
    for k, value in llist:
        if k == key:
            return value
    return None


### node properties
def get_prop(node, name):
    """
    Get properties
    """
    title = node.get('title')
    if not title:
        return None
    props = title.split(';')
    for prop in props:
        (key, args) = prop.split(None, 1)
        if key == name:
            return args
    return None


def get_bbox(node):
    """
    Get bounding box
    """
    bbox = get_prop(node, 'bbox')
    if not bbox:
        return None
    return tuple([int(x) for x in bbox.split()])


### rectangle properties
def intersect(u_r, v_r):
    """
    Intersection of two rectangles
    """
    ret = (max(u_r[0], v_r[0]), max(u_r[1], v_r[1]), min(u_r[2], v_r[2]),
        min(u_r[3], v_r[3]))
    return ret


def area(u_r):
    """
    Area of a rectangle
    """
    return max(0, u_r[2] - u_r[0]) * max(0, u_r[3] - u_r[1])


def overlaps(u_r, v_r):
    """
    Predicate: do the two rectangles overlap?
    """
    return area(intersect(u_r, v_r)) > 0


def relative_overlap(u_r, v_r):
    """
    Relative overlap
    """
    m_r = max(area(u_r), area(v_r))
    i = area(intersect(u_r, v_r))
    return float(i) / m_r


def mostly_nonoverlapping(boxes, significant_overlap=0.2):
    """
    Mostly nonoverlapping
    """
    for i in range(len(boxes)):
        for j in range(i + 1, len(boxes)):
            if relative_overlap(boxes[i], boxes[j]) > significant_overlap:
                return 0
    return 1


def main():
    """
    Main
    """
    if len(sys.argv) < 2:
        print "usage:", sys.argv[0], "[-o] file.html"
        sys.exit(1)
    optlist, args = getopt.getopt(sys.argv[1:], "o")
    nooverlap = (assoc('-o', optlist) == '')
    if len(args) == 1:
        stream = args[0]
        print "Checking '%s'...\n" % stream
    elif len(args) > 1:
        raise NameError("can only check one file at a time")
    else:
        stream = sys.stdin
    doc = parse(stream)

    ################################################################
    ### XML structure checks
    ################################################################

    # check for presence of meta information
    metareq = set(['ocr-system', 'ocr-capabilities'])
    metaopt = set(['ocr-langs', 'ocr-scripts', 'ocr-number-of-pages'])
    langs = ('ab', 'aa', 'af', 'ak', 'sq', 'am', 'ar', 'an', 'hy', 'as', 'av',
             'ae', 'ay', 'az', 'bm', 'ba', 'eu', 'be', 'bn', 'bh', 'bi', 'bjn',
             'bs', 'br', 'bg', 'my', 'ca', 'ch', 'ce', 'ny', 'zh', 'cv', 'kw',
             'co', 'cr', 'hr', 'cs', 'da', 'day', 'dv', 'nl', 'dz', 'en', 'eo',
             'et', 'ee', 'fo', 'fj', 'fi', 'fr', 'ff', 'gl', 'ka', 'de', 'el',
             'gn', 'gu', 'ht', 'ha', 'he', 'hz', 'hi', 'ho', 'hu', 'ia', 'id',
             'ie', 'ga', 'ig', 'ik', 'io', 'is', 'it', 'iu', 'ja', 'jv', 'kl',
             'kn', 'kr', 'ks', 'kk', 'km', 'ki', 'rw', 'ky', 'kv', 'kg', 'ko',
             'ku', 'kj', 'la', 'lb', 'lg', 'li', 'ln', 'lo', 'lt', 'lu', 'lv',
             'gv', 'mk', 'mg', 'ms', 'ml', 'mt', 'mi', 'mr', 'mh', 'mn', 'na',
             'nv', 'nb', 'nd', 'ne', 'ng', 'nn', 'no', 'ii', 'nr', 'oc', 'oj',
             'cu', 'om', 'or', 'os', 'pa', 'pi', 'fa', 'pl', 'ps', 'pt', 'qu',
             'rm', 'rn', 'ro', 'ru', 'sa', 'sc', 'sd', 'se', 'sm', 'sg', 'sr',
             'gd', 'sn', 'si', 'sk', 'sl', 'so', 'st', 'es', 'su', 'sw', 'ss',
             'sv', 'ta', 'te', 'tg', 'th', 'ti', 'bo', 'tk', 'tl', 'tn', 'to',
             'tr', 'ts', 'tt', 'tw', 'ty', 'ug', 'uk', 'ur', 'uz', 've', 'vi',
             'vo', 'wa', 'cy', 'wo', 'fy', 'xh', 'yi', 'yo', 'za', 'zu',
             'unknown')

    scripts = ('Afak', 'Hluw', 'Arab', 'Armn', 'Avst', 'Bali', 'Bamu', 'Bass',
               'Batk', 'Beng', 'Blis', 'Phlv', 'Bopo', 'Brah', 'Brai', 'Bugi',
               'Buhd', 'Cari', 'Cakm', 'Cham', 'Cher', 'Cirt', 'Zinh', 'Zzzz',
               'Zyyy', 'Zxxx', 'Copt', 'Xsux', 'Cprt', 'Cyrl', 'Cyrs', 'Dsrt',
               'Deva', 'Dupl', 'Egyd', 'Egyh', 'Egyp', 'Elba', 'Ethi', 'Geor',
               'Glag', 'Goth', 'Gran', 'Grek', 'Gujr', 'Guru', 'Hang', 'Hani',
               'Hans', 'Hant', 'Hano', 'Hebr', 'Hira', 'Armi', 'Inds', 'Phli',
               'Prti', 'Jpan', 'Hrkt', 'Java', 'Jurc', 'Kthi', 'Knda', 'Kana',
               'Kali', 'Khar', 'Khmr', 'Khoj', 'Sind', 'Geok', 'Kore', 'Kpel',
               'Laoo', 'Latf', 'Latg', 'Latn', 'Lepc', 'Limb', 'Lina', 'Linb',
               'Lisu', 'Loma', 'Lyci', 'Lydi', 'Mlym', 'Mand', 'Mani', 'Zmth',
               'Maya', 'Mtei', 'Mend', 'Merc', 'Mero', 'Plrd', 'Mong', 'Moon',
               'Mroo', 'Mymr', 'Nbat', 'Nkgb', 'Talu', 'Nkoo', 'Nshu', 'Ogam',
               'Olck', 'Hung', 'Ital', 'Narb', 'Perm', 'Xpeo', 'Sarb', 'Orkh',
               'Orya', 'Osma', 'Hmng', 'Palm', 'Phag', 'Phnx', 'Phlp', 'Rjng',
               'Qabx', 'Qaaa', 'Roro', 'Runr', 'Samr', 'Sara', 'Saur', 'Shrd',
               'Shaw', 'Sgnw', 'Sinh', 'Sora', 'Sund', 'Sylo', 'Zsym', 'Syrn',
               'Syre', 'Syrc', 'Syrj', 'Tglg', 'Tagb', 'Tale', 'Lana', 'Tavt',
               'Takr', 'Taml', 'Tang', 'Telu', 'Teng', 'Thaa', 'Thai', 'Tibt',
               'Tfng', 'Tirh', 'Ugar', 'Cans', 'Vaii', 'Visp', 'Wara', 'Wole',
               'Yiii','unknown')

    for metatag in metareq:
        node = doc.find(".//meta[@name='%s']" % metatag)
        if node is None:
               raise NameError("FATAL ERROR: Can not find required " + \
                            "meta tag '%s'!" % metatag)
        else:
            print "Found %s:" % metatag, node.attrib['content']

    for metatag in metaopt:
        node = doc.find(".//meta[@name='%s']" % metatag)
        content = ""
        if node is None:
           print 'WARNING: Missing optional meta tag %s' % metatag
        else:
           content = node.attrib['content']
        if metatag == 'ocr-langs' and content != "":
            if content not in langs:
                print "WARNING: Found tag '%s', but " % metatag + \
                "'%s' is not ISO 639-1 code.\n" % content + \
                "  Please check: " + \
                "http://en.wikipedia.org/wiki/List_of_ISO_639-1_codes."
            else:
                 print "Found %s:" % metatag, content
        elif metatag == 'ocr-scripts' and content != "":
            if content not in scripts:
                print "WARNING: Found tag '%s', but " % metatag + \
                "'%s' is not ISO 15924 letter code.\n" % content + \
                "  Please check: " + \
                "http://unicode.org/iso15924/iso15924-en.html."
            else:
                 print "Found %s:" % metatag, content

    #Logical Structuring Elements
    lse = set(['ocr_document',
                   'ocr_linear',
                       'ocr_title',
                       'ocr_author',
                       'ocr_abstract',
                       'ocr_part',  # [H1]
                       'ocr_chapter',  # [H1]
                           'ocr_section',
                           'ocr_sub*section',  # [H3,H4]
                               'ocr_display',
                               'ocr_blockquote',  # [BLOCKQUOTE]
                               'ocr_par'  # [P]
                               ])
    #Typesetting Related Elements
    tre = set(['ocr_page',
                   'ocr_carea',
                   'ocr_separator',
                   'ocr_noise'])

    # check for presence of page - must be present
    assert doc.xpath("//*[@class='ocr_page']") != []

    # check that lines are inside pages
    lines = doc.getroot().xpath("//*[@class='ocr_line']")
    for line in lines:
        assert line.xpath("//*[@class='ocr_page']")

    # check that pars are inside pages
    pars = doc.getroot().xpath("//*[@class='ocr_par']")
    for par in pars:
        assert par.xpath("//*[@class='ocr_page']")

    # check that columns are inside pages
    columns = doc.getroot().xpath("//*[@class='ocr_column']")
    for column in columns:
        assert column.xpath("//*[@class='ocr_page']")

    ################################################################
    ### geometric checks
    ################################################################

    if not nooverlap:
        for page in doc.xpath("//*[@class='ocr_page']"):
            # check lines
            objs = page.xpath("//*[@class='ocr_line']")
            line_bboxes = [get_bbox(obj) for obj in objs if get_prop(obj,
                'bbox')]
            assert mostly_nonoverlapping(line_bboxes)
            # check paragraphs
            objs = page.xpath("//*[@class='ocr_par']")
            par_bboxes = [get_bbox(obj) for obj in objs if get_prop(obj,
                'bbox')]
            assert mostly_nonoverlapping(par_bboxes)
            # check columns
            objs = page.xpath("//*[@class='ocr_column']")
            column_bboxes = [get_bbox(obj) for obj in objs if get_prop(obj,
                'bbox')]
            assert mostly_nonoverlapping(column_bboxes)
    print "\nEnd of checks."

if __name__ == '__main__':
    main()

################################################################
### TODO
################################################################

# FIXME add many other checks:
# - containment of paragraphs, columns, etc.
# - ocr-capabilities vs. actual tags
# - warn about text outside ocr_ elements
# - check title= attribute format
# - check that only the right attributes are present on the right elements
# - check for unrecognized ocr_ elements
# - check for significant overlaps
# - check that image files are not repeated
