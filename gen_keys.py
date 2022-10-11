import rsa

CLIENTS_COUNT = 3


def gen_keys(name):
    pubkey, privkey = rsa.newkeys(4096, accurate=True)
    with open(f'{name}/keys/{name}.pub', mode='w') as f:
        # f.write(str(pubkey.save_pkcs1(), encoding='utf8'))
        f.write(pubkey.save_pkcs1().decode('utf8'))
    with open(f'{name}/keys/{name}.key', mode='w') as f:
        # f.write(str(privkey.save_pkcs1(), encoding='utf8'))
        f.write(privkey.save_pkcs1().decode('utf8'))


print('Generating server keys...')
gen_keys('server')

for i in range(1, CLIENTS_COUNT+1):
    print(f'Generating client{i} keys...')
    gen_keys(f'client{i}')

input('All public and private keys generated. Press Enter...')
