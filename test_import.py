try:
    exec(open('utils/agent.py').read())
    print('Executed')
    print('Dir:', [x for x in dir() if not x.startswith('__')])
except Exception as e:
    print('Error during exec:', e)
    import traceback
    traceback.print_exc()