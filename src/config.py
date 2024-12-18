import os
import mercadopago
from dotenv import load_dotenv

load_dotenv()

sdk = mercadopago.SDK(os.getenv('MERCADOPAGO_ACCESS_TOKEN'))