import hashlib,hmac,secrets
CURRENT=310000;LEGACY=250000
def hash_password(p,s=None,n=CURRENT):
 s=s or secrets.token_hex(16);return s,hashlib.pbkdf2_hmac('sha256',p.encode(),s.encode(),n).hex()
def verify_password(p,s,d):return any(hmac.compare_digest(hash_password(p,s,n)[1],d) for n in (CURRENT,LEGACY))
def validate_password(v):return len(v)>=10 and any(c.isupper() for c in v) and any(c.isdigit() for c in v)
