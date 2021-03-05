import subprocess as sp
import random
config_settings = {
    'variant' : 0,
    'shell_len': 0,
    'dst_len': 0,
    'text': ''
}

full_text = []
break_text = []
def change_byte(pos, new_byte):
    full_text[pos] = new_byte


def change_text(new_text):
    config_settings['text'] = new_text


def find_delimeters():
    work_str = config_settings['text']
    delimeters = {';', '=', ',', '.'}
    for i in range(len(work_str)):
        if work_str[i] in delimeters:
            print('Founded {} at {}'.format(work_str[i], i))


def read_config(filename):
    with open(filename, 'rb') as f:
        config_text = f.read()
    config_settings['variant'] = int(config_text[0])
    config_settings['text'] = config_text[config_text.find(bytes('start', encoding='utf-8')) + len('start'):-1].decode('utf-8')
    config_settings['shell_len'] = int.from_bytes(config_text[4:8], 'little')
    config_settings['dst_len'] = int.from_bytes(config_text[8:12], 'little')
    return config_text
    #print(config_settings)

def write_config(filename, new_text):
    byte_text = bytearray(b'').join(new_text)
    with open(filename, 'wb') as f:
        f.write(byte_text)

def run_program(program):
    cmd = [program]
    ret_code = 0
    res = []
    res_str = ''
    with sp.Popen(cmd, stdout=sp.PIPE) as proc:
        res_str = str(proc.stdout.read())
        proc.wait()
        ret_code = proc.returncode
        print(res_str[res_str.find('len'):])
        input("Press Enter to continue...")
    if 'buffer' not in res_str or ret_code != 0:
        res = res_str[2:-1].split(sep='\\r\\n')
        for line in res:
            print(line)
        return True
    #res = res_str[2:-1].split(sep='\\r\\n')
    #for line in res:
    #    print(line)

def old_var(new_text):
    new_text.append(bytes([0, 0xf4]))
    new_text.append(config_settings['shell_len'].to_bytes(4, 'little'))
    new_text.append(config_settings['dst_len'].to_bytes(4, 'little'))
    new_text.append(bytes([0, 0, 0, 0]))
    new_text.append(config_settings['shell_len'].to_bytes(2, 'little'))
    new_text.append(config_settings['dst_len'].to_bytes(2, 'little'))
    new_text.append(bytes([8, 0, 0, 0]))
    new_text.append(bytes([0xb8, 0x6b, 0x33, 0]))
    new_text.append(bytes([0xb8, 0x6b, 0x33, 0]))
    new_text.append(bytes([0xb3, 0x6b, 0x33, 0]))
    new_text.append(bytes([0, 0, 0, 0]))
    new_text.append(bytes([0, 0, 0x6a, 0]))
    new_text.append(bytes([0, 0, 0x33, 0]))

    new_text.append(bytes('/start', encoding='utf-8'))
    new_text.append(config_settings['text'].encode('utf-8'))
    new_text.append(bytes([0]))


def run_tests():
    new_text = []
    new_text.append(config_settings['variant'].to_bytes(1, 'little'))
    new_text.append(config_settings['variant'].to_bytes(1, 'little'))
    for i in range(1, 48):
        new_text.append(int(0).to_bytes(1, 'little'))
    new_text.append(bytes('/start', encoding='utf-8'))
    new_text.append(config_settings['text'].encode('utf-8'))
    new_text.append(bytes([0]))

    mutate_vars = [0xff, 0xff-1, 1]
    while True:
        low = random.randint(1, 40)
        high = 0
        while high < low:
            high = random.randint(5, 48)
        for i in range(low, high):
            var = random.randint(0, len(mutate_vars) - 1)
            new_text[i] = bytes([mutate_vars[var]])
            write_config('config_2', new_text)
            res = run_program('vuln8.exe')
            if res:
                return res

if __name__ == '__main__':
    full_text = read_config('config_2_bckp')

    while True:
        res = run_tests()
        if res:
            break