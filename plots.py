#!/usr/bin/env python
# coding: utf-8


import numpy as np
import matplotlib.pyplot as plt


plt.rc('axes', color_cycle=[
    '#660000', '#00ccff', '#cc00cc', '#cc0000',
    '#00cc00', '#0000cc', '#666600'
])

plt.rc('font', **{
    'serif': 'DejaVu Serif',
    'sans-serif': 'DejaVu Sans'
})


parties = [
    u'1. Справедливая Россия',
    u'2. ЛДПР',
    u'3. Патриоты России',
    u'4. КПРФ',
    u'5. ЯБЛОКО',
    u'6. Единая Россия',
    u'7. Правое Дело'
]


def load_data(fname, region=None, uics=None):

    lines = [
        i.split(';') for i in open(fname).read().decode('utf-8').splitlines()
    ]

    try:
        int(lines[0][3])
    except ValueError:
        lines = lines[1:]

    def check(line):
        if line[2] == 0.:
            return False
        if all(int(i) == 0 for i in line[-7:]):
            return False
        if uics and int(line[1].split()[1][1:]) not in uics:
            return False
        if region and region not in line[0]:
            return False
        return True

    return np.array([list(map(int, i[2:3] + i[-7:])) for i in lines if check(i)],
                    dtype=np.float)


def presence(data):
    return data[:,1:].sum(axis=1) / data[:,0]


def presence_split(data, percent):
    d1 = np.array(filter(
        lambda d: d[1:].sum() * 100 / d[0] < percent,
        data
    ), dtype=data.dtype)
    d2 = np.array(filter(
        lambda d: d[1:].sum() * 100 / d[0] >= percent,
        data
    ), dtype=data.dtype)
    return d1, d2


def presence_gate(data, min_percent, max_percent):
    return np.array(filter(
        lambda d: min_percent < d[1:].sum() * 100 / d[0] < max_percent,
        data
    ), dtype=data.dtype)


def presence_cut(data, min_percent, max_percent):
    def check(d):
        s = d[1:].sum() * 100 / d[0]
        return (s < min_percent) or (s > max_percent)
    return np.array([d for d in data if check(d)], dtype=data.dtype)


def party_split(data, party, proc):
    d1 = np.array(filter(lambda d: d[party] * 100 / d[1:].sum() < proc, data),
                  dtype=data.dtype)
    d2 = np.array(filter(lambda d: d[party] * 100 / d[1:].sum() >= proc, data),
                  dtype=data.dtype)
    return d1, d2


def votes_per_uic_by_party_histogram(spl, d, title=None,
                                     xlabel=None, ylabel=None,
                                     dp=1000):

    if title: spl.set_title(title, fontsize='large', weight='bold')
    if xlabel: spl.set_xlabel(xlabel)
    if ylabel: spl.set_ylabel(ylabel)

    spl.set_xticks(range(0, 101, 5))
    spl.set_xlim(0, 100)
    spl.grid(True)

    s = d[:,1:].sum(axis=1)

    for i in range(1, 8):
        y, x = np.histogram(d[:,i] * 100 / s,
                            dp, (0, 100), weights=d[:,i])
        spl.plot(x[:-1], y)


def votes_by_percents_histogram(data, tr1=45., tr2=90., dp=1000):

    xlabel = u"Процент голосов на участке"
    ylabel = u"Сумма голосов на участках с данным процентом"

    splots = [plt.subplot(3, 2, i) for i in range(1, 7)]

    # 1
    votes_per_uic_by_party_histogram(
        splots[0], data,
        u"Распределение голосов по всем участкам",
        dp=dp
    )

    data2, data3 = presence_split(data, tr1)

    # 2
    votes_per_uic_by_party_histogram(
        splots[1], data2,
        u"Распределение голосов по участкам с явкой меньше %.2g%%" % tr1,
        dp=dp
    )

    # 3
    votes_per_uic_by_party_histogram(
        splots[2], data3,
        u"Распределение голосов по участкам с явкой >= %.2g%%" % tr1,
        ylabel=ylabel,
        dp=dp
    )

    # 4
    votes_per_uic_by_party_histogram(
        splots[3], presence_cut(data, tr1, tr2),
        u"Распределение голосов по участкам с явкой "
        u"<%.2g%% или > %.2g%%" % (tr1, tr2),
        dp=dp
    )

    # 5
    votes_per_uic_by_party_histogram(
        splots[4], presence_gate(data, tr1, tr2),
        u"Распределение голосов по участкам с явкой "
        u"от %.2g%% до %.2g%%" % (tr1, tr2),
        xlabel=xlabel,
        dp=dp
    )

    for i in range(7):
        splots[5].plot([], [])

    splots[5].axis('off')
    leg = splots[5].legend(parties)
    for l in leg.get_lines():
        l.set_linewidth(5)

    plt.show()
