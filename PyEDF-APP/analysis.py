import analysis_utils as eeg_utils
import argparse

filters = {
    "lowpass": eeg_utils.Butter(high_pass=False, fs=200, order=2, cutoff=30),
    "highpass": eeg_utils.Butter(high_pass=True, fs=200, order=2, cutoff=0.8),
    "SMA": eeg_utils.SMA(),
}

parser = argparse.ArgumentParser(
    prog="EEG_Analysis",
    description="Tool to analyze and compare sent and measured signal using the PyEDF tool",
)
parser.add_argument(
    "-i",
    "--input_signal",
    type=str,
    default="common_mode_sample1",
    help="Sample signal filename. Must be present in the 'edf_samples' directory",
)
parser.add_argument(
    "-t",
    "--test_signal",
    action="store_true",
    help="Use a sinusoidal test signal instead of a real EEG measurement",
)
parser.add_argument(
    "-s",
    "--sample_rate",
    type=int,
    default=200,
    help="Set the sample rate at which the signals to be analyzed",
)
parser.add_argument(
    "-c",
    "--channels",
    type=list,
    default=["Fp1", "Fp2"],
    help="List of channels to show in the plot.",
)
parser.add_argument(
    "-m",
    "--measured_signal",
    type=str,
    default="EEG_CommonSample1",
    help="Measured signal to be analyzed together with input signal",
)
parser.add_argument(
    "-f", "--filter", choices=["lowpass", "highpass", "SMA"], default=None
)

args = parser.parse_args()

if args.test_signal and args.measured_signal == "EEG_CommonSample1":
    args.measured_signal = "Sen1Hz"

input_signal = eeg_utils.generate_input_signal(
    args.measured_signal,
    args.test_signal,
    args.channels,
    resample=True,
    filter=filters[args.filter] if args.filter else None,
)
output_signal = eeg_utils.generate_output_signal(
    args.measured_signal,
    args.channel,
    resample=False,
    filter=filters[args.filter] if args.filter else None,
)

eeg_utils.plt.plot(input_signal)
eeg_utils.plt.show()

eeg_utils.plt.plot(output_signal)
eeg_utils.plt.show()
