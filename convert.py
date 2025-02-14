import json

# Cargar el archivo JSON original
with open("credentials.json", "r") as f:
    data = json.load(f)

# Convertirlo en una sola línea
json_string = json.dumps(data)

print(json_string)  # Copiar y pegar en Render

