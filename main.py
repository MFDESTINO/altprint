import matplotlib.pyplot as plt

def arrayplot(xarray, yarray):
    for i in range(len(xarray) - 1):
        x = xarray[i]
        y = yarray[i]
        dx = xarray[i + 1] - x
        dy = yarray[i + 1] - y

        plt.arrow(x, y, dx, dy,
              shape='full',
              lw=0,
              length_includes_head=True,
              head_width=.1)

def generate_scaffold(n):
    a = [0.0, 0.0]
    x = []
    y = []
    for i in range(n * 2 + 2):
        if i % 2:
            a[1] = n - a[1]
        else:
            a[0] = i / 2
        x.append(a[0])
        y.append(a[1])
    return [x, y]

def transform(xarray, yarray, n):
    u = []
    v = []
    for i in range(len(xarray)):
        x = n - yarray[i]
        y = n - xarray[i]
        u.append(x)
        v.append(y)
    return [u, v]

size = 40
asd = generate_scaffold(size)
fgh = transform(asd[0], asd[1], size)

plt.plot(asd[0], asd[1], drawstyle='steps')
plt.plot(fgh[0], fgh[1], drawstyle='steps')
'''arrayplot(fgh[0], fgh[1])'''
plt.show()
