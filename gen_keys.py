import rsa

CLIENTS_COUNT = 3


def gen_keys(name):
    pubkey, privkey = rsa.newkeys(4096, accurate=True)
    with open(f'keys/{name}.pub', mode='w') as f:
        f.write(pubkey.save_pkcs1().decode('utf8'))
    with open(f'keys/{name}.key', mode='w') as f:
        f.write(privkey.save_pkcs1().decode('utf8'))


print('Generating SERVER keys...', end='')
gen_keys('SERVER')
print('OK')

for i in range(1, CLIENTS_COUNT+1):
    print(f'Generating client{i} keys...', end='')
    gen_keys(f'client{i}')
print('OK')

input('All public and private keys generated. Press Enter...')
