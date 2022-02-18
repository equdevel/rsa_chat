import rsa

(pubkey, privkey) = rsa.newkeys(4096)

with open('public.key', mode='w') as f:
    f.write(str(pubkey.save_pkcs1(), encoding='utf8'))

with open('private.key', mode='w') as f:
    f.write(str(privkey.save_pkcs1(), encoding='utf8'))

print('Public and private keys generated. Press Enter...')
input()
