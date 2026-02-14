import os
import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException

def enviar_correo(destinatario, asunto, contenido_html):
    configuration = sib_api_v3_sdk.Configuration()
    configuration.api_key['api-key'] = os.getenv("BREVO_API_KEY")

    api_instance = sib_api_v3_sdk.TransactionalEmailsApi(
        sib_api_v3_sdk.ApiClient(configuration)
    )

    email = sib_api_v3_sdk.SendSmtpEmail(
        to=[{"email": destinatario}],
        sender={"email": "soporte@arathlabs.com", "name": "Arath Labs"},
        subject=asunto,
        html_content=contenido_html
    )

    try:
        api_instance.send_transac_email(email)
        return True
    except ApiException as e:
        print("Error al enviar correo:", e)
        return False