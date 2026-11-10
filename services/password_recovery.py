import hashlib
import secrets
from core.db import fetch_one,execute
from core.security import hash_password,validate_password
from services.mail import send_password_reset_email

RESET_MINUTES=20
GENERIC_MESSAGE='Si el correo corresponde a una cuenta activa, se enviaran las instrucciones de recuperacion.'


def _digest(value): return hashlib.sha256(value.encode('utf-8')).hexdigest()


def request_password_reset(email):
    normalized=(email or '').strip().lower()
    user=fetch_one("SELECT id,email FROM usuarios WHERE LOWER(TRIM(email))=%s AND activo=TRUE",(normalized,))
    if not user: return GENERIC_MESSAGE
    execute('UPDATE password_reset_tokens SET usado_en=NOW() WHERE usuario_id=%s AND usado_en IS NULL',(user['id'],))
    code=f'{secrets.randbelow(1000000):06d}'
    execute("INSERT INTO password_reset_tokens(usuario_id,token_hash,expira_en) VALUES(%s,%s,NOW()+(%s || ' minutes')::interval)",(user['id'],_digest(code),RESET_MINUTES))
    send_password_reset_email(user['email'],code,RESET_MINUTES)
    return GENERIC_MESSAGE


def reset_password_with_code(email,code,new_password):
    if not validate_password(new_password): raise ValueError('PASSWORD_POLICY')
    normalized=(email or '').strip().lower()
    row=fetch_one("SELECT t.id,u.id usuario_id FROM password_reset_tokens t JOIN usuarios u ON u.id=t.usuario_id "
                  "WHERE LOWER(TRIM(u.email))=%s AND t.token_hash=%s AND t.usado_en IS NULL "
                  "AND t.expira_en>NOW() AND u.activo=TRUE ORDER BY t.id DESC LIMIT 1",
                  (normalized,_digest((code or '').strip())))
    if not row: raise ValueError('INVALID_OR_EXPIRED_CODE')
    salt,digest=hash_password(new_password)
    execute('UPDATE usuarios SET salt=%s,password_hash=%s,debe_cambiar_password=FALSE,intentos_fallidos=0,bloqueado_hasta=NULL,actualizado_en=NOW() WHERE id=%s',(salt,digest,row['usuario_id']))
    execute('UPDATE password_reset_tokens SET usado_en=NOW() WHERE usuario_id=%s AND usado_en IS NULL',(row['usuario_id'],))
    return True
