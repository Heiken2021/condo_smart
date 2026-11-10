from openai import OpenAI

from core.ai.config import ai_is_configured, get_ai_api_key, get_ai_model


class AIConfigurationError(RuntimeError):
    pass


class AIClient:
    """
    Capa comun de acceso a IA de Condo_Smart.

    Los agentes de negocio dependen de esta abstraccion y no del proveedor
    directamente.
    """

    def __init__(self, model=None, client=None):
        self.model = model or get_ai_model()
        self._client = client

    @property
    def configured(self):
        return self._client is not None or ai_is_configured()

    def _get_client(self):
        if self._client is not None:
            return self._client

        api_key = get_ai_api_key()

        if not api_key:
            raise AIConfigurationError(
                "La IA no esta configurada. Falta OPENAI_API_KEY."
            )

        self._client = OpenAI(api_key=api_key)
        return self._client

    def structured_response(self, *, instructions, input_text, schema):
        client = self._get_client()

        response = client.responses.parse(
            model=self.model,
            input=[
                {
                    "role": "system",
                    "content": instructions,
                },
                {
                    "role": "user",
                    "content": input_text,
                },
            ],
            text_format=schema,
        )

        parsed = response.output_parsed

        if parsed is None:
            raise RuntimeError(
                "El proveedor de IA no devolvio una respuesta estructurada."
            )

        return parsed
