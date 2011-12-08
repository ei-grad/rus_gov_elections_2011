#!/usr/bin/env python
# coding: utf-8


import numpy as np
import matplotlib.pyplot as plt


plt.rc('font', **{
    'serif': 'DejaVu Serif',
    'sans-serif': 'DejaVu Sans'
})


def load_data(fname, region=None, uics=None):

    lines = [
        i.split(';') for i in open(fname).read().decode('utf-8').splitlines()
    ]

    try:
        int(lines[0][3])
    except ValueError:
        lines = lines[1:]

    if region:
        lines = filter(lambda x: region in x[0], lines)

    if uics:
        lines = filter(lambda x: int(x[1].split()[1][1:]) in uics, lines)

    return np.array([list(map(int, i[2:3] + i[-7:])) for i in lines],
                    dtype=np.int)


def presence_split(data, proc):
    d1 = np.array(filter(lambda d: d[1:].sum() * 100 / d[0] < proc, data))
    d2 = np.array(filter(lambda d: d[1:].sum() * 100 / d[0] >= proc, data))
    return d1, d2


def party_split(data, party, proc):
    d1 = np.array(filter(lambda d: d[party] * 100 / d[1:].sum() < proc, data))
    d2 = np.array(filter(lambda d: d[party] * 100 / d[1:].sum() >= proc, data))
    return d1, d2


def plot2(d1, d2, dp=1000):

    plt.subplot(2, 1, 1)
    for i in range(1, 7):
        y, x = np.histogram(d1[:,i] * 100 / d1[:,1:].sum(axis=1), dp, (0, 100),
                            weights=d1[:,i])
        plt.plot(x[:-1], y)

    plt.subplot(2, 1, 2)
    for i in range(1, 7):
        y, x = np.histogram(d2[:,i] * 100 / d2[:,1:].sum(axis=1), dp, (0, 100),
                            weights=d2[:,i])
        plt.plot(x[:-1], y)

    plt.show()
