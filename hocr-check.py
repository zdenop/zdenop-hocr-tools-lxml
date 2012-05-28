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
    Get bbox
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
    elif len(args) > 1:
        raise NameError("can only check one file at a time")
    else:
        stream = sys.stdin
    doc = parse(stream)

    ################################################################
    ### XML structure checks
    ################################################################

    # check for presence of meta information
    assert doc.xpath("//meta[@name='ocr-system']") != []
    assert doc.xpath("//meta[@name='ocr-capabilities']") != []

    # check for presence of page
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

if __name__ == '__main__':
    main()

################################################################
### TODO
################################################################

# FIXME add many other checks:
# - containment of paragraphs, columns, etc.
# - ocr-recognized vs. actual tags
# - warn about text outside ocr_ elements
# - check title= attribute format
# - check that only the right attributes are present on the right elements
# - check for unrecognized ocr_ elements
# - check for significant overlaps
# - check that image files are not repeated
