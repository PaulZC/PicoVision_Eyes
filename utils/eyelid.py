from xml.dom.minidom import parse
from svg.path import parse_path

# From: https://github.com/adafruit/Pi_Eyes/blob/master/gfxutil.py
def get_view_box(root):
    """Get artboard bounds (to use Illustrator terminology)
       from SVG DOM tree:"""
    for node in root.childNodes:
        if node.nodeType == node.ELEMENT_NODE:
            view_box = get_view_box(node)
            if view_box:
                return view_box
            if node.tagName.lower() == "svg":
                view_box = node.getAttribute("viewBox").split()
                return (float(view_box[0]), float(view_box[1]),
                        float(view_box[2]), float(view_box[3]))
    return None


def get_path(root, path_name):
    """Search for and return a specific path (by name) in SVG DOM tree:"""
    for node in root.childNodes:
        if node.nodeType == node.ELEMENT_NODE:
            path = get_path(node, path_name)
            if path:
                return path
            if((node.tagName.lower() == "path") and
               (node.getAttribute("id") == path_name)):
                return parse_path(node.getAttribute("d"))
    return None


def path_to_points(path, num_points, closed, reverse):
    """Convert SVG path to a 2D point list. Provide path, number of points,
       and whether or not this is a closed path (loop). For closed loops,
       the size of the point list returned is one element larger than the
       number of points passed, and the first and last elements will
       coincide."""
    points = []
    num_points = max(num_points, 2)
    if closed:
        div = float(num_points)
    else:
        div = float(num_points - 1)
    for point_num in range(num_points):
        if reverse:
            point = path.point(1.0 - point_num / div, error=1e-5)
        else:
            point = path.point(point_num / div, error=1e-5)
        points.append((point.real, point.imag))
    if closed:
        points.append(points[0])
    return points


def get_points(root, path_name, num_points, closed, reverse):
    """Combo wrapper for path_to_points(get_path(...))."""
    return path_to_points(get_path(root, path_name),
                          num_points, closed, reverse)


def scale_points(points, view_box, radius):
    """Scale a given 2D point list by normalizing to a given view box
       (returned by get_view_box()) then expanding to a given size
       centered on (0,0)."""
    for point_num, _ in enumerate(points): # Index of each point in path
        points[point_num] = (((points[point_num][0] - view_box[0]) /
                              view_box[2] - 0.5) * radius *  2.0,
                             ((points[point_num][1] - view_box[1]) /
                              view_box[3] - 0.5) * radius * -2.0)


def points_interp(points1, points2, weight2):
    """Interpolate between two 2D point lists, returning a new point list.
       Specify weighting (0.0 to 1.0) of second list. Lists should have
       same number of points; if not, lesser point count is used and the
       output may be weird."""
    num_points = min(len(points1), len(points2))
    if num_points < 1:
        return None
    weight2 = min(max(0.0, weight2), 1.0)
    weight1 = 1.0 - weight2
    points = []
    for point_num in range(num_points):
        points.append(
            (points1[point_num][0] * weight1 + points2[point_num][0] * weight2,
             points1[point_num][1] * weight1 + points2[point_num][1] * weight2))
    return points

def round_points(points):
    for point_num, _ in enumerate(points): # Index of each point in path
        points[point_num] = (round(points[point_num][0]), round(points[point_num][1]))

def invert_Y(points):
    for point_num, _ in enumerate(points): # Index of each point in path
        points[point_num] = (points[point_num][0], 0 - points[point_num][1])


dom = parse("C:/Users/pc235/Documents/GitHub/Pi_Eyes/graphics/eye.svg")

vb = get_view_box(dom)

upperLidClosedPts = get_points(dom, "upperLidClosed", 32, False, True )
upperLidOpenPts   = get_points(dom, "upperLidOpen"  , 32, False, True )
lowerLidClosedPts = get_points(dom, "lowerLidClosed", 32, False, False)
lowerLidOpenPts   = get_points(dom, "lowerLidOpen"  , 32, False, False)

eyeRadius = 48

allThePoints = [upperLidClosedPts, upperLidOpenPts, \
                lowerLidClosedPts, lowerLidOpenPts]

for point in allThePoints:
    scale_points(point, vb, eyeRadius)
    round_points(point)
    invert_Y(point)
    print (point)
