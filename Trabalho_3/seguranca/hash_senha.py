
import base64


# Constantes do FNV-1a de 64 bits.
FNV_OFFSET_BASIS = 14695981039346656037
FNV_PRIME = 1099511628211
MASCARA_64_BITS = 0xFFFFFFFFFFFFFFFF


def validar_senha(senha):
    """
    Valida uma senha alfanumerica de 6 caracteres.
    """

    if not isinstance(senha, str):
        return False

    if len(senha) != 6:
        return False

    return all(
        ("a" <= caractere <= "z")
        or ("A" <= caractere <= "Z")
        or ("0" <= caractere <= "9")
        for caractere in senha
    )


def fnv1a_64(texto):
    """
    Calcula manualmente o hash FNV-1a de 64 bits.
    """

    hash_atual = FNV_OFFSET_BASIS

    for byte in texto.encode("utf-8"):

        # Aplica XOR entre o hash e o byte atual.
        hash_atual = hash_atual ^ byte

        # Multiplica pela constante FNV.
        hash_atual = hash_atual * FNV_PRIME

        # Mantem apenas os 64 bits inferiores.
        hash_atual = hash_atual & MASCARA_64_BITS

    return hash_atual


def gerar_hash_senha(senha):
    """
    Valida a senha, calcula o hash e retorna
    uma representacao em Base64.
    """

    if not validar_senha(senha):
        raise ValueError(
            "A senha deve conter exatamente "
            "6 caracteres alfanumericos."
        )

    valor_hash = fnv1a_64(senha)

    # Converte o inteiro de 64 bits em 8 bytes.
    hash_bytes = valor_hash.to_bytes(8, byteorder="big")

    # Representa o resultado em Base64.
    hash_base64 = base64.b64encode(hash_bytes)

    return hash_base64.decode("ascii")
