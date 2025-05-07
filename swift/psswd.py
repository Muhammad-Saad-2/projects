from urllib.parse import quote_plus

password = "bnz&UM6:4x"
encoded_password = quote_plus(password)
print(encoded_password)