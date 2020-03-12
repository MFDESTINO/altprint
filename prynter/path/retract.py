def retract(x, y, f):
    """
    Splits an AB segment from a C point, between A and B. Used for creating
    an recovery zone on variable flow bridges.
    ARGS:
    x: list contaning x points from the segment (list)
    y: list contaning y points from the segment (list)
    f: factor that determines where the segment will be splited. (float)
    RETURNS:
    Tuple containg the two new segments. (tuple)
    """
    A = [x[0], y[0]]
    B = [x[1], y[1]]
    C = [A[0] + f*(B[0]-A[0]), A[1] + f*(B[1]-A[1])]
    acx = [A[0], C[0]]
    acy = [A[1], C[1]]
    cbx = [C[0], B[0]]
    cby = [C[1], B[1]]
    AC = [acx, acy]
    CB = [cbx, cby]
    return AC, CB
