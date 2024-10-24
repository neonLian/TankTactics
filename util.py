
def slope(x1, y1, x2, y2):
    return (y2 - y1) / (x2 - x1)

def y_int(x1, y1, x2, y2):
    return -1 * slope(x1,y1,x2,y2) * x1 + y1

# y = mx + b
# y - b = mx
# (y-b)/m = x

def intersectSquare(p1, p2, x, y, w):
    tl = (x, y)
    tr = (x+w, y)
    bl = (x, y+w)
    br = (x+w, y+w)

    # Horizontal line
    if p1[1] == p2[1]:
        if p1[1] >= y and p1[1] <= y+w:
            if (p1[0] < x+w and p2[0] > x) or (p2[0] < x+w and p1[0] > x):
                return True
        return False

    # Vertical line
    if p1[0] == p2[0]:
        if p1[0] >= x and p1[0] <= x+w:
            if (p1[1] < y+w and p2[1] > y) or (p2[1] < y+w and p1[1] > y):
                return True
        return False

    m = slope(p1[0], p1[1], p2[0], p2[1])
    b = y_int(p1[0], p1[1], p2[0], p2[1])

    topInt = (y-b) / m
    botInt = (y+w-b) / m
    leftInt = m*x + b
    rightInt = m*(x+w) + b

    didTopInt   = topInt >= x and topInt <= x+w and topInt >= min(p1[0], p2[0]) and topInt <= max(p1[0], p2[0])
    didBotInt   = botInt >= x and botInt <= x+w and botInt >= min(p1[0], p2[0]) and botInt <= max(p1[0], p2[0])
    didLeftInt  = leftInt >= y and leftInt <= y+w and leftInt >= min(p1[1], p2[1]) and leftInt <= max(p1[1], p2[1])
    didRightInt = rightInt >= y and rightInt <= y+w and rightInt >= min(p1[1], p2[1]) and rightInt <= max(p1[1], p2[1])

    # print(round(p1[0], 2), round(p1[1], 2), round(p2[0], 2), round(p2[1], 2), " | ", round(m, 2), round(b, 2), " | ", round(x, 2), round(y, 2), " | ", round(topInt,2), round(botInt,2), round(leftInt,2), round(rightInt,2))
    # print(didTopInt, didBotInt, didLeftInt, didRightInt)

    return didTopInt or didBotInt or didLeftInt or didRightInt
