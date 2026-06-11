# USRP X310 Analog and Digital SDR Transceiver

This repository contains GNU Radio based SDR transceiver flowgraphs for analog voice communication and digital data, image, and video transfer using USRP Ettus X310 devices.

The project demonstrates how real information is converted into a radio signal, transmitted through the air, received by another SDR device, and reconstructed on the receiver side.

In simple terms:

```text
Voice / File / Image / Video
-> Digital or analog signal processing
-> SDR transmitter
-> Antenna
-> Wireless channel
-> SDR receiver
-> Recovered voice / file / image / video
```

## Project Purpose

The purpose of this project is to build a complete SDR communication chain and make each part understandable.

This repository is designed for people who want to understand:

* How SDR systems work
* How GNU Radio flowgraphs are structured
* How voice can be transmitted using NBFM
* How digital data can be transmitted using BPSK or QPSK
* Why packet headers and CRC checks are required
* How video can be transferred using UDP and Python helper scripts
* How the system can be adapted to another SDR device

## What Is SDR?

SDR means Software Defined Radio.

In a traditional radio, many signal processing operations are done by fixed hardware.

In SDR, most of the signal processing is done in software.

In this project:

* The USRP device handles the RF input and output
* GNU Radio handles the signal processing logic
* The antenna sends and receives electromagnetic waves
* The flowgraph defines how the information is processed

The USRP is the radio hardware.

GNU Radio is the brain.

## Repository Contents

```text
analog_data_transceiver.grc
bpsk_digital_data_transceiver.grc
qpsk_digital_data_transceiver.grc
tx.py
rx.py
README.md
LICENSE
.gitignore
```

## File Descriptions

### analog_data_transceiver.grc

This flowgraph is used for analog voice communication.

It works like a walkie-talkie.

```text
Microphone
-> Audio filtering
-> NBFM modulation
-> USRP transmission
-> Wireless channel
-> USRP reception
-> NBFM demodulation
-> Speaker
```

### bpsk_digital_data_transceiver.grc

This flowgraph is used for digital data, image, and video transfer using BPSK modulation.

BPSK means Binary Phase Shift Keying.

It carries 1 bit per symbol.

BPSK is simple and robust, so it is useful for basic digital communication experiments.

### qpsk_digital_data_transceiver.grc

This flowgraph is used for digital data transfer using QPSK modulation.

QPSK means Quadrature Phase Shift Keying.

It carries 2 bits per symbol.

QPSK can provide a higher data rate than BPSK, but it is more sensitive to phase errors, frequency offset, and synchronization problems.

### tx.py

This Python script is used for video transmission.

It captures video from the computer camera, compresses the frames using H.264, packetizes the encoded video data, and sends it to GNU Radio through UDP.

### rx.py

This Python script is used for video reception.

It receives UDP packets from GNU Radio, extracts the H.264 video data, decodes it, and displays the received video stream on the screen.

## System Overview

There are three main communication modes in this project:

```text
Analog voice transmission
Digital file / image transmission
Digital video transmission
```

## Analog Voice System

The analog system behaves like a walkie-talkie.

Configured frequency:

```text
462.5625 MHz
```

Before transmitting, make sure this frequency is legal in your country and suitable for your hardware.

### Analog Transmitter Path

The upper part of the analog flowgraph is the transmitter side.

```text
Microphone
-> High Pass Filter
-> Low Pass Filter
-> Mic Gain
-> Push to Talk
-> NBFM Transmit
-> Rational Resampler
-> USRP Sink
-> Antenna
```

### Analog Receiver Path

The lower part of the analog flowgraph is the receiver side.

```text
Antenna
-> USRP Source
-> Rational Resampler
-> NBFM Receive
-> Band Pass Filter
-> Volume Control
-> Audio Sink
-> Speaker
```

## What Is NBFM?

NBFM means Narrowband Frequency Modulation.

FM is used to carry audio through the air.

It is similar to normal FM radio, but it uses a narrower bandwidth.

That makes it suitable for voice communication systems such as walkie-talkies.

```text
NBFM Transmit
Voice -> FM signal

NBFM Receive
FM signal -> Voice
```

## Audio Filtering

The voice signal is filtered before transmission.

### High Pass Filter

The high pass filter removes very low frequency sounds.

Examples:

```text
Low rumble
Microphone handling noise
Electrical hum
Deep background noise
```

### Low Pass Filter

The low pass filter removes very high frequency sounds.

Examples:

```text
Hiss
Sharp noise
Unnecessary high frequency components
```

Together, these filters keep mainly the human speech range.

## Push to Talk

The push-to-talk control decides whether the microphone audio is transmitted or muted.

```text
ptt = 1
Audio passes through

ptt = 0
Audio is multiplied by zero and becomes silent
```

This works like a real walkie-talkie button.

## Why Are There Two Channels?

The analog system can use two channels.

The `direction` control decides which channel is active.

```text
one branch  x direction
other branch x (1 - direction)
```

Only one branch is active at the same time.

This allows one side to transmit while the other side receives.

When the direction value is changed, the roles are swapped.

## Rational Resampler

Different parts of the system operate at different sample rates.

Example from the analog system:

```text
Audio side: 48 kHz
FM side: 192 kHz
USRP side: 1 MHz
```

The Rational Resampler matches these rates.

Transmit side:

```text
192000 x 125 / 24 = 1000000
```

Receive side:

```text
1000000 x 24 / 125 = 192000
```

Interpolation increases the sample rate.

Decimation decreases the sample rate.

## Digital Data System

The digital system sends files, images, or video using digital modulation.

Configured frequency:

```text
869.525 MHz
```

Before transmitting, check local radio regulations.

The general digital chain is:

```text
Data
-> Bytes
-> Packets
-> CRC
-> Header
-> BPSK or QPSK symbols
-> USRP transmission
-> Wireless channel
-> USRP reception
-> Symbol recovery
-> Packet detection
-> CRC check
-> Recovered data
```

## Digital Transmitter Path

The upper part of the digital flowgraph is the transmitter side.

```text
UDP Source or File Source
-> Stream to Tagged Stream
-> CRC32
-> Protocol Formatter
-> Tagged Stream Mux
-> Constellation Modulator
-> tx_baseband_gain
-> USRP Sink
```

### UDP Source or File Source

This block provides the data to be transmitted.

Use File Source for:

```text
TXT files
Images
Binary files
```

Use UDP Source for:

```text
Video transfer
Live data stream
```

### Stream to Tagged Stream

This block divides the continuous byte stream into packets.

For example:

```text
payload_size = 1000
```

This means each packet carries 1000 bytes of payload data.

### CRC32

CRC32 appends CRC bytes to the packet.

On the receiver side, the CRC check uses these bytes to detect corrupted packets.

If the packet is broken during transmission, the receiver can reject it.

### Protocol Formatter

This block creates the packet header.

The header contains information such as:

```text
Access code
Packet length
Payload information
```

The access code helps the receiver detect where a packet starts.

The length information helps the receiver understand how much data belongs to that packet.

### Tagged Stream Mux

This block combines the header and the payload into one complete packet.

```text
Header + Payload -> Complete packet
```

### Constellation Modulator

This block converts bits into modulation symbols.

For BPSK:

```text
Bits -> BPSK symbols
```

For QPSK:

```text
Bits -> QPSK symbols
```

### tx_baseband_gain

This parameter controls the internal amplitude of the transmitted baseband signal.

If it is too low, the transmitted signal may be weak.

If it is too high, the signal may become distorted.

### USRP Sink

This block sends the final complex baseband signal to the USRP device.

The USRP converts it to RF and transmits it from the antenna.

## Digital Receiver Path

The lower part of the digital flowgraph is the receiver side.

```text
USRP Source
-> RRC Filter
-> Symbol Sync
-> Costas Loop
-> Constellation Decoder
-> Differential Decoder
-> Correlate Access Code
-> Repack Bits
-> CRC32 Check
-> UDP Sink or File Sink
```

### USRP Source

This block receives the RF signal from the antenna.

The USRP converts the RF signal into complex baseband samples.

### RRC Filter

RRC means Root Raised Cosine.

This filter matches the pulse shaping used in the transmitter.

It helps reduce noise and improves symbol recovery.

### Symbol Sync

This block finds the correct sampling time for each symbol.

Digital data must be sampled at the right instant.

If the receiver samples too early or too late, the decoded bits may be wrong.

### Costas Loop

The Costas Loop corrects phase and frequency offset.

This is important because the transmitter and receiver oscillators are never perfectly identical.

If the constellation diagram is rotated, the Costas Loop helps rotate it back to the correct position.

### Constellation Decoder

This block converts constellation points back into bits.

### Differential Decoder

This block helps recover the original bit sequence after differential encoding.

### Correlate Access Code

This block searches for the known access code.

It tells the receiver:

```text
A packet starts here
```

### Repack Bits

This block collects bits and converts them back into bytes.

### CRC32 Check

This block checks whether the received packet is corrupted.

If the packet passes the CRC check, it is accepted.

If the packet fails the CRC check, it is discarded.

### UDP Sink or File Sink

This block outputs the recovered data.

Use File Sink for:

```text
TXT files
Images
Binary files
```

Use UDP Sink for:

```text
Video transfer
Live stream output
```

## File, Image, and Video Transfer

### Sending a TXT File or Image

To send a TXT file or an image, use:

```text
File Source
File Sink
```

Disable:

```text
UDP Source
UDP Sink
```

Make sure the correct file path is specified in the File Source block for the file that will be transmitted.

Also specify the correct output path in the File Sink block on the receiver side.

Example:

```text
Transmitter File Source: input file path
Receiver File Sink: output file path
```

### Sending Video

To send video, use:

```text
UDP Source
UDP Sink
tx.py
rx.py
```

Disable:

```text
File Source
File Sink
```

Video transfer uses the GNU Radio flowgraph together with the Python helper scripts.

## Video Transfer Workflow

### Receiver Side

Open a Linux terminal in the original directory where `rx.py` is located.

Run:

```bash
python3 rx.py
```

Then run the receiver-side GNU Radio flowgraph.

Do not run `rx.py` from an arbitrary location.

### Transmitter Side

First, run the transmitter-side GNU Radio flowgraph.

Then open a Linux terminal in the original directory where `tx.py` is located.

Run:

```bash
python3 tx.py
```

Make sure the computer camera is enabled.

If the camera is disabled by the keyboard camera key or privacy settings, `tx.py` cannot capture video.

## Simulation Mode

The project can also run in simulation mode without real SDR hardware.

Simulation-only blocks:

```text
Throttle
Prob Rate
Message Debug
Noise Source
Virtual Sink
Virtual Source
```

These blocks are only for simulation.

Keep them disabled during real USRP tests.

When doing simulation only:

```text
Enable both transmitter and receiver sides
Enable Throttle
Enable Prob Rate
Enable Message Debug
Enable Noise Source if channel noise testing is needed
Enable only the Virtual Sink and Virtual Source blocks with stream ID: "transmit"
Disable the UHD blocks
```

Do not enable random Virtual Sink or Virtual Source blocks.

## Disabled and Bypassed Blocks

Grey blocks are disabled.

Disabled blocks do not take part in the operation.

```text
Right click -> Enable
Right click -> Disable
```

Yellow blocks are bypassed.

A bypassed block can be understood as a direct wire in that position.

The signal passes through without that block affecting it.

## Throttle Block

The Throttle block is used only in simulation.

It limits the processing speed.

Without real hardware, GNU Radio may process samples as fast as the CPU allows.

Throttle prevents the simulation from running unrealistically fast.

Keep the Throttle block disabled during real USRP tests.

## Real USRP Test Mode

During real wireless tests:

```text
Enable UHD USRP Source
Enable UHD USRP Sink
Disable simulation-only blocks
Use correct SDR device addresses
Use correct antenna connections
Use suitable transmit and receive gain values
```

Do not use excessive transmit power if the USRP devices are close to each other.

## USRP Device Addresses

The UHD block addresses must be selected according to the SDR device being used.

```text
2-channel USRP X310 address:
addr=192.168.10.2

1-channel USRP Ettus X310 address:
addr=192.168.10.3
```

Both transmitter and receiver UHD blocks must use the correct device address.

## Important Parameters

### tx_baseband_gain

Controls the internal amplitude of the transmitted signal before it enters the USRP Sink.

### Transmit Gain

Controls the RF transmit power of the SDR device.

Use carefully.

If two USRP devices are close to each other, do not use high transmit gain.

### Receive Gain

Controls receiver sensitivity.

If it is too low, the receiver may not detect the signal.

If it is too high, the receiver may saturate and distort the signal.

### Time: BW

Controls the speed of the symbol timing recovery loop.

This affects the Symbol Sync block on the receiver side.

### Phase: Bandwidth

Controls the correction speed of the Costas Loop.

This affects phase and carrier recovery.

If the constellation is rotated or data does not pass the CRC check, this parameter may need adjustment.

## Constellation Diagram Troubleshooting

The constellation diagram is a very useful debugging tool.

For BPSK, the receiver should normally show 2 main points.

For QPSK, the receiver should normally show 4 main points.

If you see clear constellation points, it means the signal is being received.

However, if no data is flowing in the receiver output section, the constellation may not be interpreted correctly.

A common reason is phase shift.

To fix this:

```text
Reduce the Phase: Bandwidth parameter using the slider
Watch the constellation diagram
Adjust until the constellation reaches the correct position
Check whether bytes pass through the CRC32 check
Check whether data is written to the output file
```

When the correct position is found, the packets should pass the CRC32 check and the recovered data should be written to the output file or sent to the UDP output.

## Common Problems and Fixes

### No received file output

Check:

```text
File Sink output path
File Source input path
Receiver flowgraph status
CRC32 check result
Constellation diagram
Correct SDR address
Correct simulation or real test block selection
```

### Constellation exists but no data is written

Possible reasons:

```text
Phase shift
Wrong Costas Loop setting
Wrong Symbol Sync setting
Too much transmit power
Too much receive gain
Frequency offset
CRC failure
Wrong packet detection
```

### Video does not work

Check:

```text
rx.py is running on the receiver side
tx.py is running on the transmitter side
Both scripts are run from their original directories
The camera is enabled
UDP blocks are enabled
File Source and File Sink blocks are disabled
UDP ports match
```

### Simulation runs too fast

Enable the Throttle block.

Throttle limits processing speed during simulation.

## Adapting This Project to Another SDR Device

This project was built using USRP Ettus X310 devices, but the general communication logic can be adapted to other SDR devices.

To adapt it:

```text
Replace UHD USRP Source with the source block of your SDR
Replace UHD USRP Sink with the sink block of your SDR
Set the correct device address or device arguments
Set a supported sample rate
Set the center frequency
Set transmit and receive gains carefully
Use a legal frequency for your location
Check whether your SDR supports transmission
```

Some SDR devices are receive-only.

Receive-only SDR devices can only be used on the receiver side.

## Recommended Operating Workflow

### TXT or Image Transfer

```text
Set the input file path in File Source
Set the output file path in File Sink
Disable UDP blocks
Choose simulation mode or real USRP mode
Run the receiver side first
Run the transmitter side
Check CRC32 and output file
```

### Video Transfer

```text
Disable File Source and File Sink
Enable UDP blocks
Run rx.py on the receiver side from its original directory
Run the receiver flowgraph
Run the transmitter flowgraph
Run tx.py on the transmitter side from its original directory
Check that the camera is enabled
```

### Real USRP Test

```text
Use correct UHD addresses
Connect antennas correctly
Start with low transmit gain
Increase gain slowly if needed
Avoid placing USRP devices too close with high transmit power
Monitor constellation and CRC32 results
```

## Safety and Legal Notes

Do not transmit on arbitrary frequencies.

Always check your local frequency regulations before transmitting.

Use low transmit gain when SDR devices are close.

Use proper antennas and cables.

Avoid transmitting near sensitive equipment.

If you only want to test the signal processing chain, use simulation mode first.

## Technologies Used

```text
GNU Radio
GNU Radio Companion
Python
UHD
USRP Ettus X310
NBFM
BPSK
QPSK
CRC32
UDP streaming
H.264 video encoding
Digital packet communication
```

## Final Summary

Analog voice mode:

```text
Voice -> NBFM -> USRP -> Air -> USRP -> NBFM Receive -> Speaker
```

Digital file and image mode:

```text
File -> Packets -> CRC32 -> BPSK/QPSK -> USRP -> Air -> USRP -> Decode -> CRC32 Check -> File
```

Digital video mode:

```text
Camera -> tx.py -> UDP -> GNU Radio -> BPSK/QPSK -> USRP -> Air -> USRP -> Decode -> UDP -> rx.py -> Video Output
```

This project demonstrates a complete SDR communication system from source data to wireless transmission and back to recovered data.
