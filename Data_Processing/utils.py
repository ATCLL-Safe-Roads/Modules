from numpy import array, zeros, fabs


def __get_pixel_to_coordinates_mapping(p_id):
    if p_id == 33:
        return {
            'p1': (64, 142), 'c1': (40.632459, -8.648389),
            'p2': (485, 50), 'c2': (40.632158, -8.648347),
            'p3': (428, 336), 'c3': (40.632422, -8.648547),
            'p4': (620, 78), 'c4': (40.632099, -8.648497)
        }
    else:
        return None


def get_pixel_to_coordinates_table(p_id, w=640, h=360):
    mapping = __get_pixel_to_coordinates_mapping(p_id)
    if mapping is None:
        return None  # Unsupported p_id

    # Unpack mapping
    px1, py1 = mapping['p1']
    px2, py2 = mapping['p2']
    px3, py3 = mapping['p3']
    px4, py4 = mapping['p4']

    cx1, cy1 = mapping['c1']
    cx2, cy2 = mapping['c2']
    cx3, cy3 = mapping['c3']
    cx4, cy4 = mapping['c4']

    # Input System of Equations
    a = array([[px1, py1, 1, 0, 0, 0, (-1) * px1 * cx1, (-1) * py1 * cx1],
               [0, 0, 0, px1, py1, 1, (-1) * px1 * cy1, (-1) * py1 * cy1],
               [px2, py2, 1, 0, 0, 0, (-1) * px2 * cx2, (-1) * py2 * cx2],
               [0, 0, 0, px2, py2, 1, (-1) * px2 * cy2, (-1) * py2 * cy2],
               [px3, py3, 1, 0, 0, 0, (-1) * px3 * cx3, (-1) * py3 * cx3],
               [0, 0, 0, px3, py3, 1, (-1) * px3 * cy3, (-1) * py3 * cy3],
               [px4, py4, 1, 0, 0, 0, (-1) * px4 * cx4, (-1) * py4 * cx4],
               [0, 0, 0, px4, py4, 1, (-1) * px4 * cy4, (-1) * py4 * cy4]], float)
    b = array([cx1, cy1, cx2, cy2, cx3, cy3, cx4, cy4], float)
    n = len(b)
    x = zeros(n, float)

    # First loop specifies the fixed row
    for k in range(n - 1):
        if fabs(a[k, k]) < 1.0e-12:

            for i in range(k + 1, n):
                if fabs(a[i, k]) > fabs(a[k, k]):
                    a[[k, i]] = a[[i, k]]
                    b[[k, i]] = b[[i, k]]
                    break

        # Applies the elimination below the fixed row
        for i in range(k + 1, n):
            if a[i, k] == 0: continue

            factor = a[k, k] / a[i, k]
            for j in range(k, n):
                a[i, j] = a[k, j] - a[i, j] * factor
                # We also calculate the b vector of each row
            b[i] = b[k] - b[i] * factor

    x[n - 1] = b[n - 1] / a[n - 1, n - 1]
    for i in range(n - 2, -1, -1):
        sum_ax = 0

        for j in range(i + 1, n):
            sum_ax += a[i, j] * x[j]

        x[i] = (b[i] - sum_ax) / a[i, i]

    a = x[0]
    b = x[1]
    gama1 = x[2]
    c = x[3]
    d = x[4]
    gama2 = x[5]
    p = x[6]
    q = x[7]

    A = [[a, b, gama1],
         [c, d, gama2],
         [p, q, 1]]

    lookup = [[0 for col in range(w)] for row in range(h)]

    for l in range(0, h):
        for c in range(0, w):
            B = [[c],
                 [l],
                 [1]]

            # result will be
            result = [[sum(a * b for a, b in zip(A_row, B_col))
                       for B_col in zip(*B)]
                      for A_row in A]

            lookup[l][c] = [result[0][0] / result[2][0], result[1][0] / result[2][0]]

    return lookup
