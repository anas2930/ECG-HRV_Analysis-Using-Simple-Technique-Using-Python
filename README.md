This is a simple, step by step guide to understanding ECG (electrocardiogram) signal processing in Python. It walks through everything from loading a real heart recording, all the way to calculating meaningful heart rate numbers. It was built while learning, using the MIT BIH Arrhythmia Database, a free and widely used collection of real ECG recordings used in research.
The goal of this guide is to explain things in plain language, so that someone with basic Python knowledge but no background in biomedical signals can follow along and actually understand what is happening at each step, not just copy code.

**Results**
Running the full pipeline on Record 100 gave the following results. Detected beats: 2309. Reference beats marked by an expert cardiologist: 2273. Sensitivity: 99.60 percent. Precision: 98.05 percent. F1 Score: 98.82 percent. DER: 0.0239. SDNN: 66.09 ms. RMSSD: 90.28 ms. pNN50: 13.10 percent.

The three images below show the **raw signal, the signal after filtering, and the detected heartbeats ** compared against the expert labeled reference beats. Notice how closely the detected beats line up with the reference ones.

Raw ECG signal, first 10 seconds, Record 100.
Raw signal compared with the filtered signal, showing how much cleaner it looks after filtering.
Detected R peaks compared with the reference beats, showing very close agreement.

**Step 1: Loading the data and understanding what is inside it**
An ECG recording is not just one simple number, it comes with extra information attached to it, called metadata. This includes things like how many times per second the heart activity was measured, how long the recording is, and how many channels or leads of data were recorded.

The most important idea to understand here is sampling frequency, often written as fs. An ECG signal is not a smooth continuous line inside a computer, it is actually made up of thousands of individual voltage readings taken very quickly, one after another. In this dataset, the heart's electrical activity is measured 360 times every single second. A higher sampling frequency means more detail is captured about the heartbeat, but it also means more data to work with.
This first step is simply about getting comfortable with the data itself. How long is the recording, how many leads does it have, and what does the raw numbers actually look like before anything is done to them.

**Step 2: Visualizing the raw signal**
Before applying any processing to a signal, it is always a good idea to simply look at it first. This step creates a time axis for the signal, since the raw data by itself is just a list of numbers with no timestamps attached, and then plots the first several seconds so it can be seen visually.
The idea behind building a time axis is simple. If there are a certain number of samples taken every second, then any individual sample happened at a specific point in time, which can be calculated by dividing its position in the list by the sampling frequency.
At this stage, the signal usually looks a bit messy compared to a clean textbook ECG picture. There is often a slow wandering baseline, almost like the whole signal is gently drifting up and down, along with some sharper high frequency noise sitting on top of the actual heartbeat shape. This is completely normal and expected, and it is exactly what the next step is designed to fix.

**Step 3: Filtering the signal**
Raw ECG signals contain more than just the heartbeat, they also contain unwanted interference. This includes very slow baseline wandering caused by things like breathing or slight movement, as well as fast high frequency noise coming from muscle activity or nearby electronics.
Research has shown that the clinically useful part of an ECG waveform mostly lives between 0.5 Hz and 40 Hz. So a filter that keeps everything inside that range and removes everything outside of it cleans the signal up significantly, without losing the actual heartbeat information. This range is also commonly used with hardware ECG sensors.
The type of filter used here is called a Butterworth filter, which is a standard and well behaved filter design. It does not distort the shape of the signal much while removing noise, which matters a lot, because distorting the heartbeat shape would make later steps less accurate.
There is also an important technical detail worth understanding. The filter is applied in a special way that runs it forward through the signal and then backward again. This cancels out a side effect called phase delay, which would otherwise slightly shift the position of the heartbeats in time. Since later steps depend on precise timing between heartbeats, this correction is necessary for accurate results.

**Step 4: Detecting heartbeats and checking accuracy**
The R peak is the tall, sharp spike that appears once during every single heartbeat. It is the easiest and most reliable point to detect on an ECG signal, which is why almost every heart rate detection method is built around finding these peaks first.
This step works in three parts. First, the filtered signal is normalized, meaning it is rescaled so that its average value is zero and its variation is consistent, which allows the same detection settings to work well across different recordings. Second, a peak finding method is used, along with a rule that prevents two detected heartbeats from being impossibly close together, based on a realistic maximum heart rate. Third, and most importantly, the detected heartbeats are compared against expert labeled reference beats that come included with the dataset. These reference labels were placed by real cardiologists, so comparing against them tells us how good the detection actually is.
On Record 100, this comparison showed extremely strong results, with 99.6 percent of real heartbeats correctly detected, and 98.05 percent of all detected beats being genuinely correct. This is a strong outcome for a fairly simple detection method.

**Step 5**
If there is an additional step used between detecting heartbeats and calculating heart rate variability, it belongs here. Otherwise, this step can be skipped, and the next step becomes the final one in the sequence.

**Step 6: Heart Rate Variability analysis**
Once the exact timing of every heartbeat is known, it becomes possible to measure how much the time between heartbeats changes over time. This is called Heart Rate Variability, and it is a well studied and meaningful indicator of how the nervous system is influencing the heart.
The process starts by calculating the time gap between every pair of consecutive heartbeats, measured in milliseconds. Any gaps that fall outside a realistic physical range are removed, since these usually indicate a missed or incorrectly detected heartbeat rather than a real change in heart rhythm.
From the remaining clean data, three commonly used measurements are calculated. SDNN measures the overall variability across all heartbeat intervals. RMSSD focuses more on short term, beat to beat changes, and is calculated from the differences between consecutive intervals. pNN50 measures the percentage of times the heartbeat interval changed by more than 50 milliseconds from one beat to the next.
These three measurements are the standard starting point in heart rate variability research, and there is also a more advanced frequency based analysis that can be explored later as a natural next step.
A small technical note here. In this script, the sampling frequency is fetched from the recording itself, but then immediately replaced with a fixed value of 360. This works correctly here because this particular dataset always uses 360 as its sampling frequency, but it is worth knowing that this would need to be changed if a different recording with a different sampling frequency were used instead.

**Getting the data**
This project does not include the actual ECG recording files. Instead, they should be downloaded directly from PhysioNet, which is a free and open archive that hosts the MIT BIH Arrhythmia Database. This can be done directly from within Python using the wfdb library's built in download function, specifying Record 100.
What is MIT BIH. It is the most widely used public ECG dataset in research, made up of about 48 half hour recordings, each one digitized at 360 samples per second, and each one hand labeled beat by beat by cardiologists. It is considered the standard benchmark that most heartbeat detection research is tested against.

**A note for learners:**
This guide focuses on one lead of one recording to keep things simple and easy to follow. Every idea introduced here, sampling frequency, filtering, peak detection, and variability analysis, applies the same way to any other ECG recording, and to real hardware sensors as well. Once these fundamentals feel comfortable, trying the same steps on a different record, or comparing results between two different people's recordings, is a great way to deepen understanding.

**Helpful resources to learn more**
> PhysioNet's MIT BIH Arrhythmia Database page, which hosts the dataset itself along with full documentation.

> The wfdb python library documentation, which explains the tool used to read the recordings.

> The original 1985 paper by Pan and Tompkins titled A Real Time QRS Detection Algorithm, published in IEEE Transactions on Biomedical Engineering. This is the classic paper that most modern heartbeat detection methods are still based on in some form.

> The 1996 Heart Rate Variability standards paper published in the journal Circulation by the Task Force of the European Society of Cardiology and the North American Society of Pacing and Electrophysiology. This is the reference standard that defines SDNN, RMSSD, pNN50, and related measurements.

The AAMI EC57 standard, which defines how heartbeat detection algorithms should be tested and reported in research, including sensitivity, precision, and detection error rate.
