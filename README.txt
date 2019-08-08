Example usages:

> python Driver1.py -b 'voice' -f 'sysex' -i input_example/yamaha_tx802/ -s 'yamaha_tx802'

> python Driver1.py -b 'performance' -f 'sysex' -i input_example/yamaha_tx802/ -s 'yamaha_tx802'


DEPRECATED(?):
> python Dump.py -i test_yamaha_dx7.syx


TO DO:

- Python 3 support

- doesn't like .SYX... should be case insensitive

Test loading weird patches into dexed THEN DX7:

- weird name (non ascii), verify that it prints a name
- incorrect header + checksum syx
