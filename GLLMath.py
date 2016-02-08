import math

def pointsSubtract(p0, p1):
    return (p0[0] - p1[0], p0[1] - p1[1])

def pointsAdd(p0, p1):
    return (p1[0] + p0[0], p1[1] + p0[1])

def pointsMultiply(p0, p1):
    return (p1[0] * p0[0], p1[1] * p0[1])

def pointsDivide(p0, p1):
    return (p0[0] / p1[0], p0[1] / p1[1])

def pointLen(p):
    '''Length of the point/vector'''
    return math.sqrt(p[0] * p[0] + p[1] * p[1])

def pointNormalized(p):
    return (p[0] / pointLen(p), p[1] / pointLen(p))

def pointMultipliedByScalar(p, s):
    return (p[0] * s, p[1] *s)

def pointCross(p):
    return (p[1], -p[0])

def pointCrossAlt(p):
    return (-p[1], p[0])