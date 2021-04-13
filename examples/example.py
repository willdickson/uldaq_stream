import uldaq_stream

low_channel = 0
high_channel = 3
sample_rate = 20000          
data_file = 'data.txt'
uldaq_stream.stream(low_channel, high_channel, sample_rate, data_file)
