from telegram.main import message_loop

print('Starting...')
message_loop.run_as_thread()
print('Running!')

while not input('Enter anything to quit'):
    pass