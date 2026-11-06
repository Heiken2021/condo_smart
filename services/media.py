from io import BytesIO
from PIL import Image
ALLOWED={'image/png','image/jpeg','image/bmp'}
def validate(upload,max_mb):
 if not upload:return None
 if upload.type not in ALLOWED:raise ValueError('Formato Permitido: JPG, JPEG, PNG O BMP')
 b=upload.getvalue()
 if len(b)>max_mb*1024*1024:raise ValueError(f'El Archivo Excede {max_mb} MB')
 Image.open(BytesIO(b)).verify();return {'data':b,'mime':upload.type,'name':upload.name}
