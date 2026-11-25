# TV compatibility

Each row describes one firmware and CleanFrame build. A successful install and launch do not establish that individual features work on the TV.

| Samsung model | Tizen | Firmware | CleanFrame | Install | Launch | Remote navigation | Launch installed apps | HDMI switching | Live weather |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| UE43RU7102KXXH | 5.0 | T-MSLDEUC-1500.9 | 0.7.7 | Confirmed by TV SDK | Confirmed by TV SDK | Browser only | No physical result recorded | Browser with simulated inputs | Browser with sample data and live API from PC |

The reference result is for the locally signed launcher payload built from the same 0.7.7 source. The publicly downloadable widget requires your own app identity and Samsung signing before installation. See the [device test record](CLEANFRAME-TV.md).

## Report another model or firmware

Use the [TV compatibility report](https://github.com/Bfarkas98/tizen5.0-samsung-tv-cleanframe/issues/new?template=tv-compatibility.yml) to share working results as well as failures. Mark each result individually. For example, an HDMI report should identify whether the input was physically connected and the TV actually switched to it.
