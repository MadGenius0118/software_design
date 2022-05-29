import matplotlib.pyplot as plt
import pandas as pd
from scipy.signal import find_peaks


def raw_ecg_plot(directory):
    data = pd.read_csv(directory, header=None, names=['Time', 'Voltage'])
    plt.plot(data["Time"], data["Voltage"])
    plt.savefig("ecg_test.jpeg")
    plt.close()


def SR(data):
    fs = round(1 / (data.iloc[1, 0] - data.iloc[0, 0]), 3)
    sample = fs * 0.5
    return fs, sample


def normalize_ecg(ecg):
    ecg_norm = (ecg-ecg.min())/(ecg.max()-ecg.min())
    return ecg_norm


def R_peaks(ecg, sample):
    peaks, _ = find_peaks(ecg, height=0.41, distance=sample)
    return peaks


def hr_estimate(data, normalize_ecg, sample):
    six_strip = data['Time'] <= 6
    seg = normalize_ecg[six_strip]
    peaks = R_peaks(seg, sample)
    avg_hr = average_hr(peaks)
    return avg_hr


def average_hr(peaks):
    avg_hr = len(peaks) * 10
    return avg_hr


def heart_rate_normalization(directory):
    data = pd.read_csv(directory, header=None, names=['Time', 'Voltage'])
    fs, sample = SR(data)
    ecg_norm = normalize_ecg(data['Voltage'])
    avg_hr = hr_estimate(data, ecg_norm, sample)
    return avg_hr
