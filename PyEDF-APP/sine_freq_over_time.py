import numpy as np
import matplotlib.pyplot as plt

def plotSignal_(signal):
    """
    Method to plot the physical signal to a graph. Shows only one channel as it will be the same for all
    """
    fig, axis = plt.subplots(1)
    start_point = 0
    end_point = 85*500
    time = np.arange(0, 85, 1 / 500)
    axis.plot(time, signal[start_point:end_point], color=(
        [168/255, 193/255, 5/255]), linewidth=0.4)
    axis.set_ylabel("Amplitude [uV]", rotation=0, labelpad=30)
    axis.set_xlabel("Time [sec]", rotation=0, labelpad=30)
    plot_figure_manager = plt.get_current_fig_manager()
    plot_figure_manager.window.showMaximized()
    plt.show()


def generate_sinusoidal_waves_matching_time(amplitude, duration, frequencies, sample_rate):
        """
        Generates a single signal that contains all frequencies. Each repeated for a duration specified by parameter.
        """
        signal = np.array([])
        time= np.linspace(0, duration*len(frequencies), duration * len(frequencies) * sample_rate, endpoint=False)
        i=0
        for t in time:
            if not t%duration*sample_rate:
                #  print(f"For t={t}; i={i}")
                 i += 1
            freq = frequencies[i-1]
            wavepoint = np.sin(2 * np.pi * freq * t)
            signal = np.append(signal, wavepoint)

        # t = np.linspace(0, len(signal) / sample_rate, len(signal), endpoint=False)

        return time, signal
        t = np.linspace(0, duration*len(frequencies), duration * len(frequencies) * sample_rate, endpoint=False)
        signal = np.array([])

        # Create sinusoidal wave which iterates to the next frequency in `frequencies` every 'duration' seconds

        for frequency in frequencies:
            cycle = amplitude*np.sin(2*np.pi * frequency * np.linspace(0, duration, duration * sample_rate, endpoint=False))
            signal = np.append(signal, cycle)
        return t, signal


frequencies = [0.1, 0.2, 0.5, 0.8, 1, 2, 3, 5, 10, 15, 20, 25, 30, 35, 40, 50, 100]
# frequencies = [1, 10]
duration = 5
t, signal = generate_sinusoidal_waves_matching_time(199, duration, frequencies, sample_rate=5000)
plt.plot(t, signal)
plt.show()
# plotSignal_(signal)