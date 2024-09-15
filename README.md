# API de Escaneo de Bases de Datos con Flask

¡API de Escaneo de Bases de Datos!
Esta aplicación basada en Flask permite gestionar usuarios, autenticar, registrar conexiones a bases de datos y escanear tablas en busca de columnas sensibles.
Utiliza `JWT` para autenticación, `SQLAlchemy` para la gestión de bases de datos y `cryptography` para el cifrado de datos sensibles.

## 🚀 Instalación y Configuración

### 1. Clonar el Repositorio

```bash
git clone https://github.com/Stivenavila/Meli.git
cd Meli
```

### 2. Crear y Activar un Entorno Virtual
```bash
python -m venv venv
source venv/bin/activate  # Para Windows usa `venv\Scripts\activate`
```

### 3. Instalar Dependencias
```bash
pip install -r requirements.txt
```

### 5. Configurar Variables de Entorno
Asegúrate de configurar las siguientes variables de entorno:

```bash
export DATABASE_URI='mysql+pymysql://usuario:contraseña@localhost:puerto/nombre_bd'
export FLASK_SECRET_KEY='tu_clave_secreta'
export JWT_SECRET_KEY='tu_clave_secreta_jwt'
export ENCRYPTION_KEY='clave_de_cifrado'
```

## 💻 Uso
Para iniciar la aplicación, ejecuta:

``` bash
python app.py
```
La aplicación estará disponible en http://localhost:5000.

## 🌐 Endpoints

### 2. Registro de Usuario

URL: /api/v1/register<br>
Método: POST<br>
Descripción: Registra un nuevo usuario en la API.<br>
Cuerpo: json

```bash
{
    "username": "nombre_usuario",
    "password": "contraseña"
}
```
Respuesta:
json
```json
{
    "message": "User registered successfully",
    "user_id": "id_del_usuario"
}
```
### 2. Inicio de Sesión
URL: /api/v1/login<br>
Método: POST<br>
Descripción: Inicia sesión y devuelve un token JWT.<br>
Cuerpo: json

```bash
{
    "username": "nombre_usuario",
    "password": "contraseña"
}
```
Respuesta:
json
```bash
{
    "access_token": "tu_token_jwt"
}
```
### 3. Añadir Conexión a Base de Datos
URL: /api/v1/database<br>
Método: POST<br>
Descripción: Añade una nueva conexión a una base de datos.<br>
Headers: Authorization: Bearer <JWT_TOKEN><br>
Cuerpo: json

```bash
{
    "host": "localhost",
    "port": 3306,
    "username": "usuario",
    "password": "contraseña",
    "database_name": "nombre_bd"
}
```
Respuesta: json
```bash
{
    "id": "id_de_la_conexion"
}
```
### 4. Escanear Base de Datos
URL: /api/v1/database/scan/<id>
Método: POST<br>
Descripción: Escanea la base de datos en busca de columnas sensibles.<br>
Headers: Authorization: Bearer <JWT_TOKEN><br>
Cuerpo: json
```bash
{
    "host": "localhost",
    "port": 3306,
    "username": "usuario",
    "password": "contraseña",
    "database_name": "nombre_bd"
}
```
Respuesta: Json

```bash
{
    "message": "Scan completed",
    "sensitive_columns": [
        {
            "table_name": "nombre_tabla",
            "column_name": "nombre_columna",
            "data_type": "tipo_dato",
            "information_type": "tipo_informacion"
        }
    ],
    "all_columns": {
        "nombre_tabla": ["columna1", "columna2"]
    }
}
```
### 5. Obtener Resultados del Escaneo
URL: /api/v1/database/scan/<id><br>
Método: GET<br>
Descripción: Obtiene los resultados del escaneo de la base de datos.<br>
Headers: Authorization: Bearer <JWT_TOKEN><br>
Respuesta: json
```bash
{
    "nombre_tabla": [
        {
            "column_name": "nombre_columna",
            "data_type": "tipo_dato",
            "information_type": "tipo_informacion"
        }
    ]
}
```
## 🛠️ Manejo de Errores
La API maneja los siguientes errores:

IntegrityError: Se produce cuando hay problemas de integridad en la base de datos.<br>
KeyError: Se produce cuando se accede a una clave que no existe en el diccionario.<br>
ServerError: Errores genéricos del servidor.

## 🔍 Configuración de Logging
La API registra eventos y errores en el archivo api.log.<br>
Puedes ajustar el nivel de logging y el formato en la configuración de logging.basicConfig.
